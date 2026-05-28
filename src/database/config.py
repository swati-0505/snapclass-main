import streamlit as st
from supabase.client import create_client, Client
import os

supabase: Client=create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)
