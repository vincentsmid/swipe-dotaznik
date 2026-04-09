from httpx import AsyncClient
from starlette import status


async def test_admin_no_auth(client: AsyncClient) -> None:
    response = await client.get("/api/admin/questions")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_admin_wrong_password(client: AsyncClient) -> None:
    response = await client.get(
        "/api/admin/questions",
        auth=("admin", "wrong_password"),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_admin_wrong_username(client: AsyncClient) -> None:
    response = await client.get(
        "/api/admin/questions",
        auth=("hacker", "admin"),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_admin_valid_auth(
    client: AsyncClient,
    admin_auth: tuple[str, str],
) -> None:
    response = await client.get("/api/admin/questions", auth=admin_auth)
    assert response.status_code == status.HTTP_200_OK
