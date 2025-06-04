	# ARCHIVE CONFIRMED
	# Creates a zip file to archive photos and then empty the Photos directory
	def archive_confirmed(self):
		archive_dir='Archived_Photos'
		now=datetime.datetime.now()
#		if not os.path.exists(archive_dir): os.makedirs(archive_dir)
		Path(archive_dir).mkdir(parents=True, exist_ok=True)
		zip_path=f"{archive_dir}/Photos_Archived_{now.strftime('%Y-%m-%d_%H%M%S')}.zip"
		# Create the zip file
		Log().info(f"Attempting to archive photos to: {zip_path}....")
		try:
			with zipfile.ZipFile(zip_path, 'w') as zip_file:
				for root, _, files in os.walk(self.image_dir):
					for file in files:
						file_path=os.path.join(root, file)
						try:
							zip_file.write(file_path)
							Log().info(f"Moved {file_path} to zip file.")
						except Exception as e:
							Log().error(f"Error archiving file: {file_path}.\n Details:\n{e}")
			Log().info(f"Archiving to {file_path} completed.")
		except Exception as e:
			Log().error(f"Error archiving to {zip_path}.\n Details:\n{e}")

		# Get total size of the Archive directory
		dir_size=0
		path=Path(archive_dir)
		dir_size=sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())

		"""
		for dirpath, _, filenames in os.walk(archive_dir):
			for filename in filenames:
				file_path=os.path.join(dirpath, filename)
				dir_size+=os.path.getsize(file_path)
		"""
		dir_size=Calc().format_size(dir_size)
		success_text=f"Photos archived to: \n{archive_dir}.\nTotal size of archive: {dir_size}."
		Display().text_with_header(10, 5, "ARCHICE SUCCESSFUL", success_text)
		Log().info(success_text)
		data=Action().purge_confirmed(len(self.image_dir) , False) # False - dont need to show purge message
		return data
