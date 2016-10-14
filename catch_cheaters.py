import commands
import json
import sys


save_file = 'results.txt'

if len(sys.argv) != 2:
	print 'Usage: ' + sys.argv[0] + ' <submissions.zip>'
	exit(1)

o = commands.getoutput('ls')
if 'submissions' in o.split('\n'):
	print 'submissions/ directory already exists. Please remove this directory and try again.'
	exit(1)

if save_file in o.split('\n'):
	print save_file + ' already exists. Please remove this file and try again.'
	exit(1)

def clean_filename(filename):
	return "".join(filename.split())

def shell_quote(filename):
	return "'" + filename.replace("'", "'\\''") + "'"

def filter_projects(x):
	return {k:v for k,v in x.iteritems() if len(v) > 1}

# Store the student's projectID as the key with a list of projects that have the same ID
project_IDs = {}

# Projects that are created using the offline editor don't contain a projectID.  Store those in a list here.
no_project_ids = []

# Store the lengths of the project as the key with a list of students with that length of project as the value
project_lengths = {}

print 'Unzipping submissions...'
commands.getoutput('unzip ' + sys.argv[1] + ' -d submissions/')

print 'Unzipping individual Scratch files...'
o = commands.getoutput('ls submissions/*.sb2')

# Clean up weird filenames
print 'Cleaning up weird filenames (filenames with spaces and such)...'
for filename in o.split('\n'):
	commands.getoutput('mv ' + shell_quote(filename) + ' ' + clean_filename(filename))

o = commands.getoutput('ls submissions/*.sb2')

print 'Finding potential cheaters...'
for filename in o.split('\n'):
	# The name of the directory to unzip to (just the name of the file before the .sb2)
	student_dir = filename[:-4]
	commands.getoutput('unzip ' + filename + ' -d ' + student_dir)
	with open(student_dir + '/project.json', 'r') as f:
		a = json.loads(f.read())
		if 'projectID' in a['info']:
			projectID = a['info']['projectID']
			if projectID not in project_IDs:
				project_IDs[projectID] = []
			project_IDs[projectID].append(student_dir)
		else:
			no_project_ids.append(student_dir)
	wc = commands.getoutput('wc ' + student_dir + '/*')
	total_line = wc.split('\n')
	# Get rid of empty strings
	count = filter(lambda x: x != '', total_line[len(total_line) - 1].split(' '))
	count = count[-2]
	if count not in project_lengths:
		project_lengths[count] = []
	project_lengths[count].append(student_dir)

cheated_projects = filter_projects(project_IDs)
suspicious_projects = filter_projects(project_lengths)
with open(save_file, 'w') as save:
	save.write('Projects with the same projectID:')
	save.write('\n\n')
	save.write(json.dumps(cheated_projects, sort_keys=True, indent=4, separators=(',', ': ')))
	save.write('\n\n')
	save.write('Projects with no projectID:')
	save.write('\n\n')
	save.write(json.dumps(no_project_ids, indent=4, separators=(',', ': ')))
	save.write('\n\n')
	save.write('Projects with the same length project:')
	save.write('\n\n')
	save.write(json.dumps(suspicious_projects, sort_keys=True, indent=4, separators=(',', ': ')))

print 'Done. Output stored in ' + save_file + '.'
