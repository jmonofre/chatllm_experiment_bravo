from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    def test_signup_success(self, client: TestClient):
        """Cadastro com dados validos deve retornar token."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "teste@exemplo.com", "password": "123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["email"] == "teste@exemplo.com"
        assert "user_id" in data

    def test_signup_duplicate_email(self, client: TestClient):
        """Cadastro com email repetido deve retornar 409."""
        client.post(
            "/api/auth/signup",
            json={"email": "dup@exemplo.com", "password": "123456"},
        )
        response = client.post(
            "/api/auth/signup",
            json={"email": "dup@exemplo.com", "password": "123456"},
        )
        assert response.status_code == 409
        assert "ja cadastrado" in response.json()["detail"].lower()

    def test_signup_invalid_email(self, client: TestClient):
        """Email invalido deve retornar 422."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "invalido", "password": "123456"},
        )
        assert response.status_code == 422

    def test_signup_short_password(self, client: TestClient):
        """Senha muito curta deve retornar 422."""
        response = client.post(
            "/api/auth/signup",
            json={"email": "valido@exemplo.com", "password": "123"},
        )
        assert response.status_code == 422

    def test_login_success(self, client: TestClient):
        """Login com credenciais validas deve retornar token."""
        # Primeiro cadastra
        client.post(
            "/api/auth/signup",
            json={"email": "login@exemplo.com", "password": "123456"},
        )
        # Depois loga
        response = client.post(
            "/api/auth/login",
            json={"email": "login@exemplo.com", "password": "123456"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["email"] == "login@exemplo.com"

    def test_login_wrong_password(self, client: TestClient):
        """Senha incorreta deve retornar 401."""
        client.post(
            "/api/auth/signup",
            json={"email": "wrong@exemplo.com", "password": "123456"},
        )
        response = client.post(
            "/api/auth/login",
            json={"email": "wrong@exemplo.com", "password": "senha_errada"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Login de usuario inexistente deve retornar 401."""
        response = client.post(
            "/api/auth/login",
            json={"email": "naoexiste@exemplo.com", "password": "123456"},
        )
        assert response.status_code == 401

    def test_logout_success(self, client: TestClient):
        """Logout com token valido deve invalidar a sessao."""
        signup_resp = client.post(
            "/api/auth/signup",
            json={"email": "logout@exemplo.com", "password": "123456"},
        )
        token = signup_resp.json()["token"]

        # Logout
        response = client.post("/api/auth/logout", headers={"token": token})
        assert response.status_code == 200
        assert "sucesso" in response.json()["message"].lower()

        # Token nao deve mais funcionar no /me
        me_resp = client.get("/api/auth/me", headers={"token": token})
        assert me_resp.status_code == 401

    def test_me_authenticated(self, client: TestClient):
        """Endpoint /me retorna dados do usuario autenticado."""
        signup_resp = client.post(
            "/api/auth/signup",
            json={"email": "me@exemplo.com", "password": "123456"},
        )
        token = signup_resp.json()["token"]

        response = client.get("/api/auth/me", headers={"token": token})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@exemplo.com"
        assert "user_id" in data

    def test_me_unauthenticated(self, client: TestClient):
        """Endpoint /me sem token deve retornar 401."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_invalid_token(self, client: TestClient):
        """Endpoint /me com token invalido deve retornar 401."""
        response = client.get("/api/auth/me", headers={"token": "token_invalido"})
        assert response.status_code == 401