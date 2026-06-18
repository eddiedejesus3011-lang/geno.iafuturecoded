from flask import Flask, request, flash, redirect, url_for
import os
import requests

app = Flask(__name__)

# Todo lo demás (incluyendo el @app.route('/minar')) va AQUÍ ABAJO: