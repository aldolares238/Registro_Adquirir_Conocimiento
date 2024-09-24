#Nombre: Aldo Emiliano Chavez Lares
#Registro: 21310238
#Grupo: 7F1


import sqlite3
import os
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Base de datos principal para manejar las áreas de conocimiento
MAIN_DB = 'knowledge_areas.db'

# Conectar a la base de datos principal
main_conn = sqlite3.connect(MAIN_DB)
main_cursor = main_conn.cursor()

# Crear la tabla de áreas de conocimiento si no existe
main_cursor.execute('''
CREATE TABLE IF NOT EXISTS knowledge_areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_name TEXT UNIQUE,
    db_path TEXT
)
''')
main_conn.commit()

# Base de datos general (sin área específica)
GENERAL_DB = 'general_knowledge.db'

# Crear la base de datos general si no existe
def setup_general_db():
    conn = sqlite3.connect(GENERAL_DB)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        answer TEXT
    )
    ''')
    # Respuestas precargadas para la conversación general
    preloaded_qa = [
        ('Hola', '¡Hola! ¿Cómo estás hoy?'),
        ('Buenos días', '¡Buenos días! Espero que tu día esté yendo bien.'),
        ('Buenas tardes', '¡Buenas tardes! ¿Cómo va tu día?'),
        ('Buenas noches', '¡Buenas noches! ¿Hay algo en lo que pueda ayudarte antes de que te vayas a descansar?'),
        ('¿Cómo estás?', 'Estoy aquí para aprender y ayudarte. ¿Tienes alguna pregunta para mí?'),
        ('¿Qué puedes hacer?', 'Puedo responder tus preguntas y aprender de ti. ¿De qué tema te gustaría hablar?'),
        ('¿De qué podemos hablar?', 'Podemos hablar de cualquier cosa que quieras. ¿Hay algo que te interese o quieras saber?'),
        ('¿Puedes aprender?', 'Sí, puedo aprender de nuestras conversaciones. Cuéntame algo nuevo o hazme una pregunta.'),
        ('¿Qué sabes?', 'Sé algunas cosas básicas, pero me encantaría aprender más. Pregúntame algo o enséñame sobre un tema que conozcas bien.'),
        ('¿Qué temas conoces?', 'Estoy aprendiendo todo el tiempo. Hasta ahora, conozco un poco sobre barras energéticas, pero quiero aprender más. ¿Tienes algún tema específico en mente?'),
        ('¿Cómo funciona esto?', 'Es sencillo, puedes hacerme preguntas, y si no sé la respuesta, me encantaría aprenderla contigo.'),
        ('¿Por qué estás aquí?', 'Estoy aquí para ayudarte y aprender. Mi objetivo es mejorar cada vez que hablamos. ¿De qué te gustaría hablar?'),
        ('¿Me puedes ayudar?', 'Claro, haré lo mejor que pueda. Pregúntame lo que necesites saber.'),
        ('Dime algo interesante', 'Estoy en constante aprendizaje, así que lo interesante es que puedo aprender de ti. ¿Quieres compartir algo?'),
        ('Cuéntame algo', '¿Sabías que aprender juntos nos hace mejores? ¿Hay algo que te gustaría explorar o aprender?'),
        ('¿Sabes algo de tecnología?', 'Estoy interesado en aprender sobre tecnología. ¿Hay algo específico que te gustaría discutir?')
    ]
    for question, answer in preloaded_qa:
        cursor.execute('INSERT OR IGNORE INTO knowledge_base (question, answer) VALUES (?, ?)', (question, answer))
    conn.commit()
    conn.close()

setup_general_db()

def get_closest_match(conn, question, threshold=80):
    """Función para obtener la respuesta más cercana a la pregunta del usuario usando coincidencias aproximadas."""
    cursor = conn.cursor()
    cursor.execute('SELECT question, answer FROM knowledge_base')
    questions_answers = cursor.fetchall()
    
    # Obtener solo las preguntas de la base de datos
    questions = [qa[0] for qa in questions_answers]
    
    # Buscar la mejor coincidencia aproximada
    best_match, score = process.extractOne(question, questions, scorer=fuzz.ratio)
    
    # Verificar si la mejor coincidencia supera el umbral de similitud
    if score >= threshold:
        # Retornar la respuesta asociada a la pregunta que tuvo la mejor coincidencia
        for q, a in questions_answers:
            if q == best_match:
                return a
    return None

def add_new_knowledge(conn, question, answer):
    """Función para agregar nuevo conocimiento a la base de datos especificada."""
    cursor = conn.cursor()
    cursor.execute('INSERT INTO knowledge_base (question, answer) VALUES (?, ?)', (question, answer))
    conn.commit()

def initial_learning_phase(conn, area_name):
    """Función para realizar preguntas iniciales sobre el área de conocimiento seleccionada."""
    print(f"Chat IA: Ahora aprenderé un poco más sobre '{area_name}'.")
    initial_questions = [
        "¿Cuál es el concepto principal de este tema?",
        "¿Cuáles son los beneficios más importantes?",
        "¿Qué desafíos comunes se encuentran en este campo?",
        "¿Hay algo importante que deba saber sobre este tema?",
        "¿Cuáles son los mitos comunes o ideas erróneas sobre este tema?"
    ]
    
    for question in initial_questions:
        print(f"Chat IA: {question}")
        user_response = input("Tú: ").strip()
        add_new_knowledge(conn, question, user_response)
        print("Chat IA: ¡Gracias, he aprendido algo nuevo sobre este tema!")

def interact_with_chatbot(conn):
    """Función para que el usuario interactúe haciendo preguntas al chatbot."""
    print("Chat IA: ¡Hola! Estoy listo para responder tus preguntas sobre este tema. (Escribe 'menu' para regresar al menú principal)")
    while True:
        user_input = input("Tú: ").strip()
        
        # Opción para regresar al menú principal
        if user_input.lower() == 'menu':
            print("Chat IA: Regresando al menú principal...")
            break
        
        response = get_closest_match(conn, user_input)
        if response:
            print(f"Chat IA: {response}")
        else:
            print("Chat IA: No tengo una respuesta para eso.")
            add_new = input("¿Te gustaría agregar esta respuesta al conocimiento del sistema? (sí/no): ").strip().lower()
            if add_new == 'sí':
                new_answer = input("Por favor, ingresa la respuesta para esta pregunta: ").strip()
                add_new_knowledge(conn, user_input, new_answer)
                print("Chat IA: Gracias, he aprendido algo nuevo.")

def knowledge_area_interaction(conn, area_name):
    """Función para manejar la interacción con un área de conocimiento específica."""
    while True:
        print(f"\n=== {area_name} ===")
        print("1. Enseñar al Chatbot")
        print("2. Hacer preguntas al Chatbot")
        print("3. Regresar al menú de áreas")
        choice = input("Selecciona una opción: ").strip()
        
        if choice == '1':
            initial_learning_phase(conn, area_name)
        elif choice == '2':
            interact_with_chatbot(conn)
        elif choice == '3':
            print("Regresando al menú de áreas de conocimiento...")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")

def list_knowledge_areas():
    """Función para listar las áreas de conocimiento disponibles."""
    main_cursor.execute('SELECT area_name FROM knowledge_areas')
    areas = main_cursor.fetchall()
    return [area[0] for area in areas]

def add_knowledge_area():
    """Función para agregar una nueva área de conocimiento."""
    area_name = input("Introduce el nombre de la nueva área de conocimiento: ").strip()
    db_path = f"{area_name.lower().replace(' ', '_')}_knowledge.db"
    
    # Crear una nueva base de datos para el área
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        answer TEXT
    )
    ''')
    conn.commit()
    conn.close()
    
    # Registrar el área en la base de datos principal
    main_cursor.execute('INSERT INTO knowledge_areas (area_name, db_path) VALUES (?, ?)', (area_name, db_path))
    main_conn.commit()
    print(f"El área de conocimiento '{area_name}' ha sido creada y está lista para aprender.")

def knowledge_area_menu():
    """Función para mostrar el menú de áreas de conocimiento y seleccionar una para chatear."""
    areas = list_knowledge_areas()
    if not areas:
        print("No hay áreas de conocimiento disponibles. Agrega una nueva primero.")
        return
    
    print("\n=== Áreas de Conocimiento ===")
    for idx, area in enumerate(areas, 1):
        print(f"{idx}. {area}")
    
    try:
        choice = int(input("Selecciona un área para interactuar: ").strip())
        if 1 <= choice <= len(areas):
            area_name = areas[choice - 1]
            main_cursor.execute('SELECT db_path FROM knowledge_areas WHERE area_name = ?', (area_name,))
            db_path = main_cursor.fetchone()[0]
            conn = sqlite3.connect(db_path)
            knowledge_area_interaction(conn, area_name)
            conn.close()
        else:
            print("Selección inválida.")
    except ValueError:
        print("Selección inválida.")


def chat(db_path, area_name="General"):
    """Función de chat que permite la interacción con la base de datos de conocimiento."""
    conn = sqlite3.connect(db_path)
    print(f"Chat IA ({area_name}): ¡Hola! Estoy listo para hablar contigo. (Escribe 'menu' para regresar al menú principal)")
    
    while True:
        user_input = input("Tú: ").strip()
        
        # Opción para regresar al menú principal
        if user_input.lower() == 'menu':
            print("Chat IA: Regresando al menú principal...")
            break
        
        # Intentar encontrar una respuesta en la base de datos
        response = get_closest_match(conn, user_input)
        
        if response:
            print(f"Chat IA: {response}")
        else:
            print("Chat IA: No tengo una respuesta para eso.")
            add_new = input("¿Te gustaría agregar esta respuesta al conocimiento del sistema? (sí/no): ").strip().lower()
            if add_new == 'sí':
                new_answer = input("Por favor, ingresa la respuesta para esta pregunta: ").strip()
                add_new_knowledge(conn, user_input, new_answer)
                print("Chat IA: Gracias, he aprendido algo nuevo.")
    
    conn.close()

def teach_chatbot(conn, area_name):
    """Función para que el usuario enseñe al chatbot sobre un área de conocimiento."""
    while True:
        print(f"\n=== Enseñar al Chatbot sobre {area_name} ===")
        print("1. Dejar que el Chatbot haga preguntas")
        print("2. Proporcionar un subtema directamente")
        print("3. Regresar al menú de áreas")
        choice = input("Selecciona una opción: ").strip()

        if choice == '1':
            initial_learning_phase(conn, area_name)
        elif choice == '2':
            subtopic = input("Introduce el subtema que quieres enseñar: ").strip()
            user_response = input(f"¿Cuál es la información clave sobre '{subtopic}'? ").strip()
            add_new_knowledge(conn, subtopic, user_response)
            print(f"Chat IA: Gracias, he aprendido sobre '{subtopic}'.")
        elif choice == '3':
            print("Regresando al menú de áreas de conocimiento...")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")

def knowledge_area_interaction(conn, area_name):
    """Función para manejar la interacción con un área de conocimiento específica."""
    while True:
        print(f"\n=== {area_name} ===")
        print("1. Enseñar al Chatbot")
        print("2. Hacer preguntas al Chatbot")
        print("3. Regresar al menú de áreas")
        choice = input("Selecciona una opción: ").strip()

        if choice == '1':
            teach_chatbot(conn, area_name)
        elif choice == '2':
            interact_with_chatbot(conn)
        elif choice == '3':
            print("Regresando al menú de áreas de conocimiento...")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")



def main_menu():
    """Menú principal del sistema de chat."""
    while True:
        print("\n=== Menú Principal ===")
        print("1. Conversación normal")
        print("2. Aprender en área de conocimiento")
        print("3. Agregar nueva área de conocimiento")
        print("4. Salir")
        choice = input("Selecciona una opción: ").strip()
        
        if choice == '1':
            chat(GENERAL_DB)
        elif choice == '2':
            knowledge_area_menu()
        elif choice == '3':
            add_knowledge_area()
        elif choice == '4':
            print("Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("Opción no válida, por favor intenta de nuevo.")

# Iniciar el menú principal
main_menu()
