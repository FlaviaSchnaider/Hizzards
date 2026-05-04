import sys

def interpretar_instrucao(inst_hex):
    return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python riscv_hazards.py <arquivo.hex>")
        sys.exit(1)

if __name__ == '__main__':
    main()