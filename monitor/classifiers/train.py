
import sys

sys.path.insert(0, '.')
import model

def main():
    c = model.Classification.retrain()

if __name__ == '__main__':
    main()
