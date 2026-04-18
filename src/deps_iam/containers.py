from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import (
    IMessageProducer,
    IMessageUoW,
    MessageUoW,
    MessageUoWProducer,
)
from deps_message_flow.sagas.orchestration import *
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer
from transactional_messaging import IMessageRepository, MessageRepository
from transactional_outbox import TOProducer

from deps_iam.constants import PROJECT_NAME
from deps_iam.domain.model import IPolicyRepository
from deps_iam.domain.model.policy.statement import RequestParsingService
from deps_iam.domain.services import (
    AuthorizationService,
    CustomizationService,
    EmailSender,
    InitializationService,
    OrganisationService,
    PermissionService,
    RegistrationService,
    RoleService,
    UserService,
)
from deps_iam.domain.services.access_token_auth_service import AccessTokenAuthService
from deps_iam.events_handler.consumer import make_consumer
from deps_iam.extras.auth.api_key import APIKeyAuthService
from deps_iam.extras.auth.deps_auth import DepsAuthService
from deps_iam.extras.auth.deps_jwt import JWTAuthService
from deps_iam.extras.datasource import Database
from deps_iam.extras.datasource.connection_provider import ConnectionProvider
from deps_iam.extras.datasource.constants import DBDialect, DBDriver
from deps_iam.extras.datasource.uow import DatabaseUoW
from deps_iam.extras.interfaces import IUoW
from deps_iam.infrastructure.access_management.access_managers import (
    OrganisationAccessManager,
)
from deps_iam.infrastructure.access_management.service_accessors import (
    OrganisationServiceAccessor,
)
from deps_iam.infrastructure.repositories import (
    OrganisationRepository,
    PermissionRepository,
    RoleRepository,
    SagaInstanceRepository,
    UserApiKeyRepository,
    UserRepository,
)
from deps_iam.infrastructure.repositories.policy import PolicyRepository
from deps_iam.infrastructure.uow import UnitOfWork
from deps_iam.messaging.sagas_data import *

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class DatabaseResource(resources.Resource):
    def init(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect,
        driver: DBDriver,
        require_secure_transport: bool,
        sslkey: str,
        sslcert: str,
        sslrootcert: str,
        sslmode: str,
    ) -> Database:
        db = Database(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            dialect=dialect,
            driver=driver,
            require_secure_transport=require_secure_transport,
            sslkey=sslkey,
            sslcert=sslcert,
            sslrootcert=sslrootcert,
            sslmode=sslmode,
        )
        db.connect()

        return db

    def shutdown(self, resource: Database) -> None:
        resource.close()


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()
    datasources = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )

    message_repo: providers.Singleton[IMessageRepository] = providers.Singleton(
        MessageRepository,
        connection_provider=datasources.connection_provider,
    )
    transactional_outbox_producer: providers.Provider[IMessageProducer] = providers.Singleton(
        TOProducer,
        message_repo=message_repo,
        uow=datasources.database_uow,
    )

    true_producer = providers.Selector(
        config.messaging.messaging_mode,
        broker=producer,
        transactional_outbox=transactional_outbox_producer,
    )

    message_uow: providers.Singleton[IMessageUoW] = providers.Singleton(
        MessageUoW,
        message_producer=true_producer,
    )
    message_uow_producer: providers.Singleton[IMessageProducer] = providers.Singleton(
        MessageUoWProducer,
        uow=message_uow,
    )


class DomainEventPublishers(containers.DeclarativeContainer):
    messaging = providers.DependenciesContainer()

    publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.message_uow_producer,
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_datasource: providers.Provider[Database] = providers.Resource(
        DatabaseResource,
        username=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.db,
        dialect=config.dialect,
        driver=config.driver,
        require_secure_transport=config.require_secure_transport,
        sslkey=config.ssl.key,
        sslcert=config.ssl.cert,
        sslrootcert=config.ssl.rootcert,
        sslmode=config.ssl.mode,
    )

    datasource = postgres_datasource

    connection_provider: providers.Provider[ConnectionProvider] = providers.Singleton(
        ConnectionProvider,
        database=postgres_datasource,
    )

    database_uow: providers.Provider[IUoW] = providers.Singleton(
        DatabaseUoW,
        connection_provider=connection_provider,
    )


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()
    config = providers.Configuration()

    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        datasources.datasource,
    )

    user: providers.Singleton[UserRepository] = providers.Singleton(
        UserRepository,
        database=datasources.datasource,
    )

    organisation: providers.Singleton[OrganisationRepository] = providers.Singleton(
        OrganisationRepository,
        database=datasources.datasource,
    )

    role: providers.Singleton[RoleRepository] = providers.Singleton(
        RoleRepository,
        database=datasources.datasource,
        default_organisation=config.authentication.default_organisation,
    )

    permission: providers.Singleton[PermissionRepository] = providers.Singleton(
        PermissionRepository,
        database=datasources.datasource,
    )

    user_api_key: providers.Singleton[UserApiKeyRepository] = providers.Singleton(
        UserApiKeyRepository,
        database=datasources.datasource,
    )
    policy: providers.Singleton[IPolicyRepository] = providers.Singleton(
        PolicyRepository, database=datasources.datasource
    )


class UnitOfWorks(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    datasources = providers.DependenciesContainer()
    messaging = providers.DependenciesContainer()
    domain_event_publisher: providers.Provider[DomainEventPublisher] = providers.Dependency()

    uow: providers.Singleton[UnitOfWork] = providers.Singleton(
        UnitOfWork,
        database_uow=datasources.database_uow,
        message_uow=messaging.message_uow,
        role_repository=repositories.role,
        organisation_repository=repositories.organisation,
        user_repository=repositories.user,
        user_api_key_repository=repositories.user_api_key,
        permission_repository=repositories.permission,
        event_publisher=domain_event_publisher,
    )


class DomainServiceAccessManagers(containers.DeclarativeContainer):
    unit_of_works = providers.DependenciesContainer()
    config = providers.Configuration()

    organisation: providers.Singleton[OrganisationAccessManager] = providers.Singleton(
        OrganisationAccessManager,
        uow=unit_of_works.uow,
    )


class Services(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    unit_of_works = providers.DependenciesContainer()
    infrastructure_services = providers.DependenciesContainer()
    config = providers.Configuration()
    messaging = providers.DependenciesContainer()

    role: providers.Singleton[RoleService] = providers.Singleton(
        RoleService,
        uow=unit_of_works.uow,
    )

    customization: providers.Singleton[CustomizationService] = providers.Singleton(
        CustomizationService, config.default_customization_url
    )
    user: providers.Singleton[UserService] = providers.Singleton(
        UserService,
        uow=unit_of_works.uow,
        customization_service=customization,
    )

    organisation: providers.Singleton[OrganisationService] = providers.Singleton(
        OrganisationService,
        uow=unit_of_works.uow,
        user_service=user,
    )

    permission = providers.Singleton(
        PermissionService,
        uow=unit_of_works.uow,
    )

    registration: providers.Singleton[RegistrationService] = providers.Singleton(
        RegistrationService,
        uow=unit_of_works.uow,
        user_service=user,
        org_service=organisation,
    )

    authorization: providers.Singleton[AuthorizationService] = providers.Singleton(
        AuthorizationService,
        enable_personal_org=config.authentication.enable_personal_org,
        api_key_auth_enabled=config.authentication.api_key_auth_enabled,
        access_token_auth_service=infrastructure_services.access_token_auth_service,
        register_service=registration,
        user_service=user,
    )

    consumer: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_consumer,
        messaging.consumer,
        messaging.producer,
    )

    email_sender: providers.Singleton[EmailSender] = providers.Singleton(
        EmailSender,
        login=config.smtp.login,
        password=config.smtp.password,
        host=config.smtp.host,
        port=config.smtp.port,
        from_addr=config.smtp.from_address,
        event_type=config.smtp.event_type,
        external_url=config.external_url,
        user_guide_link=config.user_guide_link,
        vpn_disclaimer=config.vpn_disclaimer,
        uow=unit_of_works.uow,
    )

    initialization: providers.Singleton[InitializationService] = providers.Singleton(
        InitializationService,
        organisation_service=organisation,
        user_service=user,
    )


class DomainServiceAccessors(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    domain_service_access_managers = providers.DependenciesContainer()

    config = providers.Configuration()

    organisation: providers.Factory[OrganisationServiceAccessor] = providers.Factory(
        OrganisationServiceAccessor,
        organisation_service=services.organisation,
        organisation_access_manager=domain_service_access_managers.organisation,
    )


class InfrastructureServices(containers.DeclarativeContainer):
    config = providers.Configuration()

    jwt_auth_service: providers.Singleton[JWTAuthService] = providers.Singleton(
        JWTAuthService,
        certs_endpoint=config.authentication.certs_endpoint,
        encryption_algorithm=config.authentication.encryption_algorithm,
        verify_ssl=config.authentication.verify_ssl,
    )

    api_key_auth_service: providers.Singleton[APIKeyAuthService] = providers.Singleton(
        APIKeyAuthService,
        api_key=config.authentication.api_key,
    )
    access_token_auth_service: providers.Singleton[AccessTokenAuthService] = providers.Singleton(
        AccessTokenAuthService,
        userinfo_endpoint=config.authentication.userinfo_endpoint,
        verify_ssl=config.authentication.verify_ssl,
    )
    deps_auth_service: providers.Singleton[DepsAuthService] = providers.Singleton(
        DepsAuthService,
        jwt_auth_service=jwt_auth_service,
        api_key_auth_service=api_key_auth_service,
    )
    request_parsing: providers.Singleton[RequestParsingService] = providers.Singleton(RequestParsingService)


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)
    core: providers.Container[Core] = providers.Container(
        Core,
        config=config,
    )
    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )
    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        datasources=datasources,
        config=config,
    )
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )
    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
        datasources=datasources,
    )
    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.message_uow_producer,
    )
    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.message_uow_producer,
    )
    saga_command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        SagaCommandProducer,
        command_producer,
    )
    saga_data_mapping: providers.Singleton[SagaDataMapping] = providers.Singleton(
        make_saga_data_mapping,
    )
    saga_manager_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaManagerFactory,
        repositories.saga_instance,
        command_producer,
        messaging.consumer,
        saga_command_producer,
        saga_data_mapping,
    )
    sagas = providers.List()
    saga_instance_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )

    unit_of_works: providers.Container[UnitOfWorks] = providers.Container(
        UnitOfWorks,
        datasources=datasources,
        repositories=repositories,
        messaging=messaging,
        domain_event_publisher=domain_event_publisher,
    )

    infrastructure_services: providers.Container[InfrastructureServices] = providers.Container(
        InfrastructureServices,
        config=config,
    )
    domain_service_access_managers: providers.Container[DomainServiceAccessManagers] = providers.Container(
        DomainServiceAccessManagers,
        unit_of_works=unit_of_works,
        config=config,
    )
    services: providers.Container[Services] = providers.Container(
        Services,
        repositories=repositories,
        unit_of_works=unit_of_works,
        infrastructure_services=infrastructure_services,
        messaging=messaging,
        config=config,
    )
    domain_service_accessors: providers.Container[DomainServiceAccessors] = providers.Container(
        DomainServiceAccessors,
        services=services,
        domain_service_access_managers=domain_service_access_managers,
        config=config,
    )
