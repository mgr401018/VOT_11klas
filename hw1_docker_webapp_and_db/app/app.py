from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER', 'myuser')}:{os.getenv('POSTGRES_PASSWORD', 'mypassword')}@db:5432/{os.getenv('POSTGRES_DB', 'mydatabase')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True, index=True)
    integer_value = Column(Integer, unique=True, nullable=False)
    string_value = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_data():
    try:
        data = request.json
        integer_value = data.get("integer")
        string_value = data.get("string")

        if integer_value is None or string_value is None:
            return jsonify({"error": "Both integer and string values are required"}), 400

        session = SessionLocal()
        new_data = Data(integer_value=integer_value, string_value=string_value)
        session.add(new_data)
        session.commit()
        session.close()
        return jsonify({"message": "Data added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_data():
    try:
        integer_value = request.args.get("integer")
        
        if integer_value is None:
            return jsonify({"error": "Integer value is required"}), 400

        session = SessionLocal()
        result = session.query(Data).filter(Data.integer_value == integer_value).first()
        session.close()

        if result:
            return jsonify({"integer": result.integer_value, "string": result.string_value}), 200
        else:
            return jsonify({"message": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update', methods=['PUT'])
def update_data():
    try:
        data = request.json
        integer_value = data.get("integer")
        string_value = data.get("string")

        if integer_value is None or string_value is None:
            return jsonify({"error": "Both integer and string values are required to update"}), 400

        session = SessionLocal()
        existing_data = session.query(Data).filter(Data.integer_value == integer_value).first()

        if not existing_data:
            session.close()
            return jsonify({"error": "No data found to update for the given integer value"}), 404

        existing_data.string_value = string_value
        session.commit()
        session.close()

        return jsonify({"message": "Data updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
