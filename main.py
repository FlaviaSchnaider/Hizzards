import json
import sys

# conversão de hexadecimal para inteiro e extração de opcode
def interpretar_instrucao(inst_hex):
    inst_hex = inst_hex.strip()
    if not inst_hex:
        return None

    try:
        inst = int(inst_hex, 16)
    except ValueError:
        return None

    opcode = inst & 0x7F
    rd = (inst >> 7) & 0x1F
    rs1 = (inst >> 15) & 0x1F
    rs2 = (inst >> 20) & 0x1F

    return {
        'hex': inst_hex,
        'valor': inst,
        'opcode': opcode,
        'rd': rd,
        'rs1': rs1,
        'rs2': rs2
    }

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
            inst = interpretar_instrucao(linha)
            
            if inst:
                instrucoes.append(inst)

    print(json.dumps(instrucoes, indent=4))

if __name__ == '__main__':
    main()