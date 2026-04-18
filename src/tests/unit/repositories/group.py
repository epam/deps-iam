def test_save_new_group__group_saved(fake_group_repository, group_factory):
    fake_group_repository.save(group_factory)

    assert len(fake_group_repository._db) == 1
    assert fake_group_repository._db[group_factory.id.value] == group_factory


def test_save_group__group_exists__group_saved(fake_group_repository, group_factory):
    fake_group_repository._db[group_factory.id.value] = group_factory
    fake_group_repository.save(group_factory)

    assert len(fake_group_repository._db) == 1
    assert fake_group_repository._db[group_factory.id.value] == group_factory
