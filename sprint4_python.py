import sys

# Para aumentar o limite de recursão na versão puramente recursiva
sys.setrecursionlimit(2000)

# --- Parâmetros do Problema ---
# Custos
CUSTO_FIXO_PEDIDO = 50  # (K) Custo administrativo/frete por pedido
CUSTO_POR_UNIDADE = 2   # (c) Custo de compra por item
CUSTO_ARMAZENAGEM = 1   # (h) Custo por item em estoque no fim do dia
CUSTO_FALTA = 10        # (p) Penalidade alta por item em falta

# Restrições
HORIZONTE_DIAS = 30     # (T) Período de planejamento
ESTOQUE_MAXIMO = 100    # (I_max) Capacidade máxima de armazenamento
ESTOQUE_INICIAL = 20    # (i_0) Estoque no dia 0

# Previsão de Demanda Diária (d_t)
# Em um cenário real, isso viria de um modelo de forecasting
demanda_diaria = [15, 20, 10, 25, 18, 30, 12, 15, 22, 17,
                  28, 19, 13, 21, 24, 16, 26, 11, 19, 23,
                  20, 27, 14, 18, 22, 25, 15, 20, 10, 30]

# --- 1. Versão Recursiva Pura ---
def solve_recursive(t, i):
    """Calcula o custo mínimo de forma recursiva."""
    if t == HORIZONTE_DIAS:
        return 0

    min_custo = float('inf')

    # Itera sobre todas as decisões possíveis (quanto pedir)
    for x in range(ESTOQUE_MAXIMO - i + 1):
        # --- Calcula os custos imediatos para a decisão x ---
        custo_pedido = (CUSTO_FIXO_PEDIDO + CUSTO_POR_UNIDADE * x) if x > 0 else 0
        
        demanda_atual = demanda_diaria[t]
        estoque_apos_pedido = i + x

        custo_armazenagem = CUSTO_ARMAZENAGEM * max(0, estoque_apos_pedido - demanda_atual)
        custo_falta = CUSTO_FALTA * max(0, demanda_atual - estoque_apos_pedido)

        custo_imediato = custo_pedido + custo_armazenagem + custo_falta
        
        # --- Transição para o próximo estado ---
        proximo_estoque = max(0, estoque_apos_pedido - demanda_atual)
        
        custo_futuro = solve_recursive(t + 1, proximo_estoque)
        
        min_custo = min(min_custo, custo_imediato + custo_futuro)
        
    return min_custo

# --- 2. Versão com Memorização (Top-Down) ---
memo = {} # Cache para armazenar resultados (t, i) -> custo

def solve_memoization(t, i):
    """Calcula o custo mínimo usando recursão com memorização."""
    if t == HORIZONTE_DIAS:
        return 0
    if (t, i) in memo:
        return memo[(t, i)]

    min_custo = float('inf')

    # Itera sobre todas as decisões possíveis (quanto pedir)
    for x in range(ESTOQUE_MAXIMO - i + 1):
        custo_pedido = (CUSTO_FIXO_PEDIDO + CUSTO_POR_UNIDADE * x) if x > 0 else 0
        
        demanda_atual = demanda_diaria[t]
        estoque_apos_pedido = i + x

        custo_armazenagem = CUSTO_ARMAZENAGEM * max(0, estoque_apos_pedido - demanda_atual)
        custo_falta = CUSTO_FALTA * max(0, demanda_atual - estoque_apos_pedido)

        custo_imediato = custo_pedido + custo_armazenagem + custo_falta
        
        proximo_estoque = max(0, estoque_apos_pedido - demanda_atual)
        
        custo_futuro = solve_memoization(t + 1, proximo_estoque)
        
        min_custo = min(min_custo, custo_imediato + custo_futuro)
        
    memo[(t, i)] = min_custo
    return min_custo

# --- 3. Versão Iterativa (Bottom-Up) ---
def solve_bottom_up():
    """Calcula o custo mínimo e a política ótima de forma iterativa."""
    # dp[t][i] armazena o custo mínimo do dia t até o fim, com estoque i
    dp = [[0] * (ESTOQUE_MAXIMO + 1) for _ in range(HORIZONTE_DIAS + 1)]
    
    # politica[t][i] armazena a decisão ótima (quanto pedir)
    politica = [[0] * (ESTOQUE_MAXIMO + 1) for _ in range(HORIZONTE_DIAS)]

    # Itera de trás para frente no tempo
    for t in range(HORIZONTE_DIAS - 1, -1, -1):
        # Itera sobre todos os possíveis níveis de estoque
        for i in range(ESTOQUE_MAXIMO + 1):
            min_custo = float('inf')
            melhor_x = 0

            # Itera sobre todas as decisões possíveis
            for x in range(ESTOQUE_MAXIMO - i + 1):
                custo_pedido = (CUSTO_FIXO_PEDIDO + CUSTO_POR_UNIDADE * x) if x > 0 else 0
                
                demanda_atual = demanda_diaria[t]
                estoque_apos_pedido = i + x

                custo_armazenagem = CUSTO_ARMAZENAGEM * max(0, estoque_apos_pedido - demanda_atual)
                custo_falta = CUSTO_FALTA * max(0, demanda_atual - estoque_apos_pedido)

                custo_imediato = custo_pedido + custo_armazenagem + custo_falta
                
                proximo_estoque = max(0, estoque_apos_pedido - demanda_atual)
                
                custo_total = custo_imediato + dp[t + 1][proximo_estoque]
                
                if custo_total < min_custo:
                    min_custo = custo_total
                    melhor_x = x
            
            dp[t][i] = min_custo
            politica[t][i] = melhor_x
            
    # Recupera a política ótima a partir do estado inicial
    politica_otima = []
    estoque_atual = ESTOQUE_INICIAL
    for t in range(HORIZONTE_DIAS):
        pedido = politica[t][estoque_atual]
        politica_otima.append((t, estoque_atual, pedido))
        
        demanda = demanda_diaria[t]
        estoque_apos_pedido = estoque_atual + pedido
        estoque_atual = max(0, estoque_apos_pedido - demanda)

    return dp[0][ESTOQUE_INICIAL], politica_otima

# --- Garantia de Resultados ---
if __name__ == "__main__":
    print("Iniciando cálculos...")

    # A versão recursiva é muito lenta para um horizonte grande,
    # então usamos um horizonte menor apenas para demonstração de igualdade.
    HORIZONTE_DIAS_CURTO = 5
    demanda_curta = demanda_diaria[:HORIZONTE_DIAS_CURTO]
    
    # Redefine o escopo global para a função recursiva de teste
    globals()['HORIZONTE_DIAS'] = HORIZONTE_DIAS_CURTO
    globals()['demanda_diaria'] = demanda_curta
    
    # Custo_rec = solve_recursive(0, ESTOQUE_INICIAL) # Pode ser extremamente lento
    
    memo.clear()
    custo_memo_curto = solve_memoization(0, ESTOQUE_INICIAL)
    
    # Redefine para o problema principal
    globals()['HORIZONTE_DIAS'] = 30
    globals()['demanda_diaria'] = [15, 20, 10, 25, 18, 30, 12, 15, 22, 17,
                                   28, 19, 13, 21, 24, 16, 26, 11, 19, 23,
                                   20, 27, 14, 18, 22, 25, 15, 20, 10, 30]
    
    custo_iterativo_curto, _ = solve_bottom_up() # Temporariamente recalcula com T curto

    print(f"\n--- Verificação de Igualdade (Horizonte T={HORIZONTE_DIAS_CURTO}) ---")
    print(f"Custo Mínimo (Memorização): {custo_memo_curto:.2f}")
    # O resultado iterativo precisa ser recalculado para o horizonte curto
    globals()['HORIZONTE_DIAS'] = HORIZONTE_DIAS_CURTO
    globals()['demanda_diaria'] = demanda_curta
    custo_iterativo_curto, _ = solve_bottom_up()
    print(f"Custo Mínimo (Iterativo):   {custo_iterativo_curto:.2f}")
    assert abs(custo_memo_curto - custo_iterativo_curto) < 1e-9, "Resultados não são iguais!"
    print("Resultados da versão com memorização e iterativa são idênticos. (Sucesso!)")

    # Resolve o problema completo (T=30)
    print("\n--- Resolvendo o Problema Completo (Horizonte T=30) ---")
    globals()['HORIZONTE_DIAS'] = 30
    globals()['demanda_diaria'] = [15, 20, 10, 25, 18, 30, 12, 15, 22, 17,
                                   28, 19, 13, 21, 24, 16, 26, 11, 19, 23,
                                   20, 27, 14, 18, 22, 25, 15, 20, 10, 30]

    custo_total_otimo, politica_execucao = solve_bottom_up()
    print(f"\nCusto Total Mínimo para {HORIZONTE_DIAS} dias: {custo_total_otimo:.2f}")
    print("\nPolítica de Reposição Ótima (Dia, Estoque no Início, Pedido):")
    for dia, estoque, pedido in politica_execucao:
        if pedido > 0:
            print(f"Dia {dia:2d}: Com {estoque:3d} itens, PEDIR {pedido:3d} unidades.")
        else:
            print(f"Dia {dia:2d}: Com {estoque:3d} itens, NÃO pedir.")