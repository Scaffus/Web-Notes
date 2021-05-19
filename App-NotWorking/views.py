from flask import request, url_for, redirect, render_template, flash
from flask.blueprints import Blueprint
from .app import create_app

app = create_app()

@app.route('/')
def index():
    return 'working'