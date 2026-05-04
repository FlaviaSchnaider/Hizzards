import sys

def interpretar_instrucao(inst_hex):
    return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.hex>")
        sys.exit(1)

    # leitura do arquivo .hex
    arquivo = sys.argv[1]
    instrucoes = []

    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue

            instrucoes.append(linha)

    print(instrucoes)

if __name__ == '__main__':
    main()