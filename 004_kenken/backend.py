from flask import Flask, jsonify, request
from kenken_puzzle_generator import KenKenGenerator
from flask_cors import CORS, cross_origin  # Import CORS
import random

app = Flask(__name__)
from flask_cors import CORS  # Import CORS

@app.route('/generate', methods=['GET'])
@cross_origin(origins='*', methods=['GET', 'POST'])
def generate_puzzle():
    """API endpoint to generate a KenKen puzzle."""
    try:
        size = request.args.get('size', default=random.randint(6, 9), type=int)
        if size < 6 or size > 9:
            return jsonify({"error": "Size must be between 6 and 9"}), 400
        
        generator = KenKenGenerator(size)
        puzzle = generator.get_puzzle()
        print(jsonify(puzzle))
        return jsonify(puzzle)
    except Exception as e:
        print(f"Error: {e}")  # Debug log
        return jsonify({"error": "Failed to generate puzzle"}), 500

if __name__ == '__main__':
    app.run(debug=True)
