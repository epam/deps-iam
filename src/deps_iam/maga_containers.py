from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration import (
    SagaCommandProducer,
    SagaDataMapping,
    SagaInstanceFactory,
    SagaManagerFactory,
)
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_iam.application import GroupService, PolicyService, UserService
from deps_iam.application.sign_up_service import SignUpService
from deps_iam.domain.model import (
    IGroupRepository,
    IIdentityProvider,
    IPolicyRepository,
    ITenantRepository,
    IUserRepository,
)
from deps_iam.extras.datasource import Database
from deps_iam.extras.datasource.constants import DBDialect, DBDriver
from deps_iam.infrastructure.repositories.saga.saga_instance import (
    SagaInstanceRepository,
)
from deps_iam.infrastructure.services import OpenIdIdentityProvider
from deps_iam.messaging.sagas import SignUpSaga
from deps_iam.messaging.sagas_data.sign_up_steps import SignUpSteps
from deps_iam.messaging.sagas_data.util import make_saga_data_mapping
from tests.fakes import (
    FakeGroupRepository,
    FakePolicyRepository,
    FakeTenantRepository,
    FakeUserRepository,
)

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


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()

    group: providers.Singleton[IGroupRepository] = providers.Singleton(FakeGroupRepository)
    tenant: providers.Singleton[ITenantRepository] = providers.Singleton(FakeTenantRepository)
    user: providers.Singleton[IUserRepository] = providers.Singleton(FakeUserRepository)
    policy: providers.Singleton[IPolicyRepository] = providers.Singleton(
        FakePolicyRepository,
    )
    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        datasources.postgres_datasource,
    )


class InfrastructureServices(containers.DeclarativeContainer):
    config = providers.Configuration()

    identity_provider: providers.Singleton[IIdentityProvider] = providers.Singleton(
        OpenIdIdentityProvider,
        userinfo_endpoint=config.authentication.userinfo_endpoint,
        verify_ssl=config.authentication.verify_ssl,
    )


class Services(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    infrastructure_services = providers.DependenciesContainer()

    group: providers.Singleton[GroupService] = providers.Singleton(
        GroupService,
        tenant_repository=repositories.tenant,
        group_repository=repositories.group,
    )

    user: providers.Singleton[UserService] = providers.Singleton(
        UserService,
        identity_provider=infrastructure_services.identity_provider,
        tenant_repository=repositories.tenant,
        user_repository=repositories.user,
    )
    policy: providers.Singleton[PolicyService] = providers.Singleton(
        PolicyService,
        policy_repository=repositories.policy,
    )


class SagaSteps(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    infrastructure_services = providers.DependenciesContainer()

    sign_up: providers.Singleton[SignUpSteps] = providers.Singleton(
        SignUpSteps,
        group_service=services.group,
        user_service=services.user,
        policy_service=services.policy,
        identity_provider=infrastructure_services.identity_provider,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)
    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )
    repositories: providers.Container[Repositories] = providers.Container(Repositories, datasources=datasources)
    infrastructure_services: providers.Container[InfrastructureServices] = providers.Container(
        InfrastructureServices, config=config
    )
    services: providers.Container[Services] = providers.Container(
        Services,
        repositories=repositories,
        infrastructure_services=infrastructure_services,
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
    )
    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )
    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
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
    saga_steps: providers.Container[SagaSteps] = providers.Container(
        SagaSteps, services=services, infrastructure_services=infrastructure_services
    )

    sagas = providers.List(
        providers.Singleton(
            SignUpSaga,
            steps=saga_steps.sign_up,
            personal_space_enabled=config.authentication.enable_personal_org,
        )
    )
    saga_instance_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )

    sign_up_service: providers.Singleton[SignUpService] = providers.Singleton(
        SignUpService,
        sagas=sagas,
        saga_instance_factory=saga_instance_factory,
    )
