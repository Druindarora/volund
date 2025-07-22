from unittest.mock import Mock, patch

from modules.parlia.services.action_service import (
    copy_chatrelay_text,
    copy_text,
    copy_to_clipboard,
)


@patch("modules.parlia.services.action_service.QApplication.clipboard")
def test_copy_to_clipboard(mock_clipboard):
    # Arrange
    mock_clipboard_instance = Mock()
    mock_clipboard.return_value = mock_clipboard_instance
    text = "Test text"

    # Act
    copy_to_clipboard(text)

    # Assert
    mock_clipboard_instance.setText.assert_called_once_with(text)
    print("Test passed: copy_to_clipboard")


@patch("modules.parlia.services.action_service.copy_to_clipboard")
def test_copy_chatrelay_text(mock_copy_to_clipboard):
    # Arrange
    expected_text = "[ChatRelay]"

    # Act
    copy_chatrelay_text()

    # Assert
    mock_copy_to_clipboard.assert_called_once_with(expected_text)
    print("Test passed: copy_chatrelay_text")


@patch("modules.parlia.services.action_service.copy_to_clipboard")
def test_copy_text(mock_copy_to_clipboard):
    # Arrange
    mock_transcription_panel = Mock()
    mock_transcription_panel.get_transcription_text.return_value = "Transcription text"

    # Act
    copy_text(mock_transcription_panel)

    # Assert
    mock_copy_to_clipboard.assert_called_once_with("Transcription text")
    print("Test passed: copy_text")
