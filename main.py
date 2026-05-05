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
    if opcode == 0x33:
        tipo = 'R'
    elif opcode in [0x13, 0x03, 0x67]:
        tipo = 'I'
    elif opcode == 0x23:
        tipo = 'S'
    elif opcode == 0x63:
        tipo = 'B'
    elif opcode in [0x37, 0x17]:
        tipo = 'U'
    elif opcode == 0x6F:
        tipo = 'J'

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
        'rd': registrador_escrito,
        'rs1': rs1,
        'rs2': rs2,
        'leitura': registradores_lidos,
        'eh_desvio': eh_desvio,
        'eh_salto': eh_salto,
        'eh_load': eh_load,
        'tipo': tipo,
        'eh_nop': inst == 0x00000013
    }


def detectar_conflitos(instrs, forwarding=False):
    conflitos = []

    for i, inst in enumerate(instrs):
        for r in inst['leitura']:
            for dist in range(1, 4):
                if i - dist >= 0:
                    anterior = instrs[i - dist]

                    if anterior['rd'] == r:
                        if not forwarding:
                            conflitos.append(f"RAW x{r} entre {i-dist} e {i}")
                        else:
                            # só penaliza load-use
                            if anterior['eh_load'] and dist == 1:
                                conflitos.append(f"Load-use x{r} entre {i-dist} e {i}")
                        break

    return conflitos

def simular_pipeline(instrs):
    novas_instrs = []
    historico = []

    NOP = interpretar_instrucao("00000013")
    NOP['eh_nop'] = True

    for inst in instrs:
        nops_necessarios = 0

        for r in inst['leitura']:
            for dist in range(1, 4):
                if len(historico) >= dist:
                    anterior = historico[-dist]

                    if anterior['rd'] == r and not anterior['eh_nop']:
                        nops_necessarios = max(nops_necessarios, 3 - dist)
                        break

        # inserir NOPs
        for _ in range(nops_necessarios):
            nop = dict(NOP)
            novas_instrs.append(nop)
            historico.append(nop)

        novas_instrs.append(inst)
        historico.append(inst)

    return novas_instrs

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.hex>")
        sys.exit(1)

    arquivo = sys.argv[1]
    instrucoes = []

    with open(arquivo, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue

            inst = interpretar_instrucao(linha)
            if inst:
                instrucoes.append(inst)

    print("\nSem forwarding:")
    print(detectar_conflitos(instrucoes, forwarding=False))

    print("\nCom forwarding:")
    print(detectar_conflitos(instrucoes, forwarding=True))

    print("\nPipeline (sem correções):")
    pipeline = simular_pipeline(instrucoes)

    for i, inst in enumerate(pipeline):
        print(i, inst['hex'])


if __name__ == '__main__':
    main()