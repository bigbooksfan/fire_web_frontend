def add_journal_row():
	ret = '''
	<tr>
		<td>
			Time
		</td>
		<td>
			Action name
		</td>
		<td>
			Status
		</td>
	</tr>
	'''
	return ret

	
def add_table_zone(name):
	return "<tr style=\"height:80px\"><td style=\"width:310px\">{}</td></tr>".format(name)
	
def add_train(board_id, loop_id):
	return "<tr style=\"height:80px\"><td style=\"width:310px\">board {} / loop {}</td></tr>".format(board_id, loop_id)
