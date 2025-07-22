# Ajoute les tests pour toutes les fonctions du fichier `chatgptService.py` directement ici, dans le fichier courant.
# N’écris aucun autre fichier, pas de répertoire `tests/`, juste le code à coller ici-même.

from unittest.mock import patch

from modules.parlia.services.chatgptService import (
    format_files_for_chatgpt,
    send_to_tracker_via_api,
)


@patch("modules.parlia.services.chatgptService.requests.post")
def test_send_to_tracker_via_api(mock_post):
    # Arrange
    mock_post.return_value.status_code = 200
    message = "Test message"

    # Act
    result = send_to_tracker_via_api(message)

    # Assert
    mock_post.assert_called_once()
    assert result is True
    print("Test passed: send_to_tracker_via_api")


@patch("modules.parlia.services.chatgptService.open")
def test_format_files_for_chatgpt(mock_open):
    # Arrange
    mock_open.return_value.__enter__.return_value.read.return_value = "File content"
    file_paths = ["file1.txt", "file2.txt"]

    # Act
    result = format_files_for_chatgpt(file_paths)

    # Assert
    assert "File content" in result
    print("Test passed: format_files_for_chatgpt")
