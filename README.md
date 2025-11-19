# Documentação da Optativa de Criptografia

Este repositório consolida os materiais práticos da disciplina optativa de Criptografia Aplicada, ofertada em 19/11. Ele reúne implementações simples de cifras clássicas e algoritmos de criptoanálise para que os alunos possam experimentar conceitos como permutações, heurísticas linguísticas e metaheurísticas computacionais.

**Grupo: Lucas de Luccas, André Hutzler e Diogo Burgierman.**
---

## 1. Estrutura do Repositório

| Caminho | Descrição |
| --- | --- |
| `permutacao_livre.py` | Implementa a cifra de permutação em blocos, um avaliador estatístico de inglês (`EnglishScorer`) e um quebra-código via algoritmo genético (`GeneticBreaker`). |
| `quebra_substituicao.py` | Ferramentas para normalização de texto, heurísticas linguísticas e um quebra-cifra de substituição monoalfabética baseado em hill-climbing com *simulated annealing*. |
| `test_breaker.py` | Pequeno *test harness* usado em aula para validar o *GA breaker* com diferentes cenários. |
| `src/crypto_breaker` | Pasta reservada para empacotamento futuro (ainda sem módulos públicos). |

---

## 2. Pré-requisitos e Setup Rápido

1. **Python**: versão 3.10+ recomendada.
2. **Ambiente virtual (opcional, mas recomendado)**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   ```
3. **Dependências**:
   ```bash
   pip install nltk
   ```
4. **Corpora do NLTK** (necessário para `EnglishScorer`):
   ```python
   >>> import nltk
   >>> nltk.download("words")
   ```
   O download ocorre automaticamente na primeira execução de `permutacao_livre.py`, mas pode ser feito previamente para evitar atrasos em sala.

---

## 3. Roteiro Pedagógico Sugerido

1. **Revisão teórica**: princípios de cifras por permutação e substituição, fragilidades conhecidas e papel das estatísticas linguísticas.
2. **Exploração guiada de `permutacao_livre.py`**:
   - Inspeção da classe `PermutationCipher`.
   - Observação de como o `EnglishScorer` usa vocabulário e bigramas para pontuar mensagens.
   - Discussão sobre operadores genéticos adotados (torneio, *crossover* tipo PMX e mutação por troca).
3. **Atividade prática**:
   - Cada grupo escolhe uma chave de permutação e cifra um texto curto.
   - Troca de mensagens entre grupos e uso do `GeneticBreaker` para tentar recuperar a chave.
4. **Criptoanálise avançada com `quebra_substituicao.py`**:
   - Explicar o chute inicial por frequência.
   - Mostrar como a busca local explora vizinhos gerados por trocas de mapeamento.
   - Debater limitações e quando integrar modelos de linguagem (gancho `evaluate_with_llm`).
5. **Encerramento**: executar `test_breaker.py` para consolidar o entendimento e incentivar melhorias.

---

## 4. Como Executar os Scripts

### 4.1 Cifra de Permutação + Algoritmo Genético

```bash
python permutacao_livre.py
```

Sugestão de atividades:
- Modifique a chave (`key = [3,1,4,2]`, etc.) e observe o efeito sobre o texto cifrado.
- Ajuste parâmetros do `GeneticBreaker` (`population_size`, `mutation_rate`, `generations`) e compare a qualidade das mensagens decriptadas.

### 4.2 Quebra de Substituição Monoalfabética

```bash
python quebra_substituicao.py
```

O script solicitará um texto cifrado. Cole a mensagem (sem quebras de linha) e acompanhe o resultado:
- `score_text` combina palavras comuns, bigramas e proporção de vogais.
- `break_general_substitution_english` roda múltiplos *restarts* com combinações de heurísticas e retorna o melhor candidato.

### 4.3 Testes de Regressão

```bash
python test_breaker.py
```

O módulo confirma se o *GA breaker*:
- Produz textos legíveis (`score > 0`).
- Mantém o tamanho das mensagens.
- É razoavelmente consistente em execuções distintas.

Use-o sempre que alterar operadores genéticos ou parâmetros para garantir que o desempenho mínimo foi preservado.

---

## 5. Extensões e Trabalhos Sugeridos

- **Empacotamento**: organizar `src/crypto_breaker` como pacote instalável com `pyproject.toml`.
- **LLM Scoring**: implementar `evaluate_with_llm` ligando um classificador do Hugging Face para ranquear candidatos de decriptação corporativa.
- **Novos corpora**: adaptar `EnglishScorer` para português (usar `nltk.corpus.mac_morpho` ou listas próprias de palavras/bigramas).
- **Interface gráfica ou notebook**: criar um *playground* em Jupyter para tornar os experimentos mais interativos.
- **Benchmarking**: comparar GA x simulated annealing x força bruta em blocos pequenos.


