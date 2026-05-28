from src.database.config import supabase
import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode('utf-8'), hashed.encode('utf-8'))

def check_teacher_exist(username):
    response=supabase.table("teachers").select("username").eq("username",username).execute()
    return len(response.data) > 0

def create_teacher(username,password,name):
    data={
        "username":username,
        "password":hash_pass(password),
        "name":name
    }
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username,password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if len(response.data) == 0:
        return False, "Teacher not found"
    
    teacher = response.data[0]
    if bcrypt.checkpw(password.encode('utf-8'), teacher['password'].encode('utf-8')):
        return True, teacher
    else:
        return False, "Incorrect password"
    

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data
def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {
        "name": new_name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }
    response = supabase.table("students").insert(data).execute()
    return response.data
