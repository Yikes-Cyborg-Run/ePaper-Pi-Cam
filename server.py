from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, socket

# Enter the IP address of your camera below
IPAddr='xxx.xxx.xxx.xxx'

app=Flask(__name__)
PHOTO_FOLDER='/home/pi/ePaper-Pi-Cam/Photos'
app.config['PHOTO_FOLDER']=PHOTO_FOLDER

ARCHIVE_FOLDER='/home/pi/ePaper-Pi-Cam/Archived_Photos'
app.config['ARCHIVE_FOLDER']=ARCHIVE_FOLDER

@app.route('/')
def index():
    files=os.listdir(app.config['PHOTO_FOLDER'])
    archives=os.listdir(app.config['ARCHIVE_FOLDER'])
    return render_template('index.html', files=files, archives=archives)

@app.route('/download/<filename>')
def download_ind(filename):
    return send_from_directory(app.config['PHOTO_FOLDER'], filename, as_attachment=True)

@app.route('/<filename>')
def download_archive(filename):
    return send_from_directory(app.config['ARCHIVE_FOLDER'], filename, as_attachment=True)

def serve(app):
    app.run(host=IPAddr, port=5000, debug=True) # Run on all interfaces, default port

if __name__=='__main__':
    serve(app)
