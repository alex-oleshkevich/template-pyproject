# from starlette.testclient import TestClient
#
# from tests.conftest import ManagerTestClient
#
#
# def test_select_organization_page_accessible(client: TestClient) -> None:
#     client.post('/login', data={'email': 'me@me.com', 'password': 'password'})
#     response = client.get('/organizations/select')
#     assert response.status_code == 200
#
#
# def test_switches_organizations(manager_client: ManagerTestClient) -> None:
#     print(manager_client.user.id)
#     response = manager_client.get('/organizations/select')
#     assert response.status_code == 200
#
#     response = manager_client.post(
#         '/organizations/select', data={'organization_id': manager_client.organization.id}, follow_redirects=False
#     )
#     assert response.status_code == 302
#     assert response.headers['location'] == '/manage/'
