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
                            if anterior['eh_load'] and dist == 1:
                                conflitos.append(f"Load-use x{r} entre {i-dist} e {i}")
                        break

    return conflitos

def simular_pipeline(instrs, forwarding=False):
    novas_instrs = []
    historico = []

    NOP = interpretar_instrucao("00000013")
    NOP['eh_nop'] = True

    nops_dados = 0
    nops_controle = 0

    for inst in instrs:
        nops_necessarios = 0

        # HAZARD DE DADOS
        for r in inst['leitura']:
            for dist in range(1, 4):
                if len(historico) >= dist:
                    anterior = historico[-dist]

                    if anterior['rd'] != -1 and anterior['rd'] == r and not anterior['eh_nop']:
                        if not forwarding:
                            nops_necessarios = max(nops_necessarios, 3 - dist)
                        else:
                            if anterior['eh_load'] and dist == 1:
                                nops_necessarios = max(nops_necessarios, 1)
                        break

        # inserir NOPs
        for _ in range(nops_necessarios):
            nop = dict(NOP)
            nop['motivo'] = 'dados'
            novas_instrs.append(nop)
            historico.append(nop)
            nops_dados += 1

        nova = dict(inst)
        novas_instrs.append(nova)
        historico.append(nova)

        # HAZARD DE CONTROLE
        if inst['eh_desvio'] or inst['eh_salto']:
            for _ in range(2):  # penalidade fixa
                nop = dict(NOP)
                nop['motivo'] = 'controle'
                novas_instrs.append(nop)
                historico.append(nop)
                nops_controle += 1

    return novas_instrs, nops_dados, nops_controle


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

    print("\nPipeline sem forwarding:")
    pipeline, nops_dados, nops_ctrl = simular_pipeline(instrucoes, forwarding=False)
    print("NOPs dados:", nops_dados)
    print("NOPs controle:", nops_ctrl)

    print("\nPipeline com forwarding:")
    pipeline, nops_dados, nops_ctrl = simular_pipeline(instrucoes, forwarding=True)
    print("NOPs dados:", nops_dados)
    print("NOPs controle:", nops_ctrl)

    print("\nPipeline detalhado:")
    pipeline, _, _ = simular_pipeline(instrucoes)

    for i, inst in enumerate(pipeline):
        if inst.get('eh_nop'):
            print(i, "NOP", inst.get('motivo', ''))
        else:
            print(i, inst['hex'])


if __name__ == '__main__':
    main()