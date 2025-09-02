import sys

from interface.router import Router


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args]")
        sys.exit(1)

    Router.execute(sys.argv)


if __name__ == "__main__":
    main()
