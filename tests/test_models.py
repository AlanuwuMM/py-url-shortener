from app.models import Urls


def test_create_url_model(db):
    """El modelo debe guardar y recuperar correctamente short_url/long_url."""
    entry = Urls(short_url='abc123', long_url='https://example.com')
    db.session.add(entry)
    db.session.commit()

    fetched = Urls.query.filter_by(short_url='abc123').first()
    assert fetched is not None
    assert fetched.long_url == 'https://example.com'
    assert fetched.id is not None


def test_url_model_repr(db):
    """__repr__ debe incluir el short_url para facilitar debugging."""
    entry = Urls(short_url='xyz789', long_url='https://example.org')
    db.session.add(entry)
    db.session.commit()

    assert 'xyz789' in repr(entry)


def test_short_url_is_unique(db):
    """La restricción unique=True debe impedir short_urls duplicados."""
    import pytest
    from sqlalchemy.exc import IntegrityError

    db.session.add(Urls(short_url='dup001', long_url='https://a.com'))
    db.session.commit()

    db.session.add(Urls(short_url='dup001', long_url='https://b.com'))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
