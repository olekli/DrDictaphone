# Copyright 2023 Ole Kliemann
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from chat_gpt import ChatGpt
from read_context import readContext
import logger_config

ok_text = 'Das ist ein Beispiel Text in deutscher Sparche, der ein paar Relative einfache Fehler enthält. ChatGpt sollte ohne weiteres in der Lage sein diese Fehleer zu korriegeren.'

err_text = 'foo smrgl grrr eta ie 1234k eit ieonai  23423nt '

ok_result = 'Das ist ein Beispieltext in deutscher Sprache, der ein paar relativ einfache Fehler enthält. ChatGPT sollte ohne weiteres in der Lage sein, diese Fehler zu korrigieren.'

@pytest.mark.integration
def test_useful_input_produces_ok_result():
  gpt = ChatGpt(readContext('context/proofread-de.yaml'))
  result = gpt.ask(ok_text)

  assert 'ok' in result
  assert not 'err' in result
  assert result['ok'] == ok_result

@pytest.mark.integration
def test_broken_input_produces_err_result():
  gpt = ChatGpt(readContext('context/proofread-de.yaml'))
  result = gpt.ask(err_text)

  assert 'err' in result
  assert not 'ok' in result
