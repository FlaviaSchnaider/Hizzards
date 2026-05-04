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

    tipo = 'DESCONHECIDO'
    
    eh_desvio = opcode == 0x63
    eh_salto = opcode in [0x6F, 0x67]
    eh_load = opcode == 0x03

    registradores_lidos = []
    registrador_escrito = -1

    if tipo == 'R':
        registradores_lidos = [rs1, rs2]
        registrador_escrito = rd

    elif tipo == 'I':
        registradores_lidos = [rs1]
        registrador_escrito = rd

    elif tipo == 'S':
        registradores_lidos = [rs1, rs2]

    elif tipo == 'B':
        registradores_lidos = [rs1, rs2]

    elif tipo == 'U':
        registrador_escrito = rd

    elif tipo == 'J':
        registrador_escrito = rd

    registradores_lidos = [r for r in registradores_lidos if r != 0]
    if registrador_escrito == 0:
        registrador_escrito = -1

    return {
        'hex': inst_hex,
        'valor': inst,
        'opcode': opcode,
        'rd': rd,
        'rs1': rs1,
        'rs2': rs2
    }

def detectar_conflitos(instrs):
    conflitos = []

    for i, inst in enumerate(instrs):
        for r in inst['leitura']:
            for j in range(max(0, i-3), i):
                anterior = instrs[j]
                if anterior['rd'] == r:
                    conflitos.append(f"Conflito entre {j} e {i}")

    return conflitos

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