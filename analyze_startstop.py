import data as d
import util as u
import pandas as pd
import plotly.express as px
import os
from multiprocessing import Process

def drawit(label, df, filepath, filename):
  first_time = df.groupby('pseudonym')['md.started_at'].min().dt.date
  first_time = first_time.value_counts()
  last_time = df.groupby('pseudonym')['md.finished_at'].max().dt.date
  last_time = last_time.value_counts()

  fig = px.bar(first_time, title = f'{label}<br>Number of volunteers making first classification on date')
  fig.write_image(filepath + '/static/' + filename + '_firstday.svg', width = 1600, height = 1200)
  fig.write_image(filepath + '/static/' + filename + '_firstday.png', width = 1600, height = 1200)
  fig.write_html(filepath + '/dynamic/' + filename + '_firstday.html')

  fig = px.bar(last_time, title = f'{label}<br>Number of volunteers making final classification on date')
  fig.write_image(filepath + '/static/' + filename + '_lastday.svg', width = 1600, height = 1200)
  fig.write_image(filepath + '/static/' + filename + '_lastday.png', width = 1600, height = 1200)
  fig.write_html(filepath + '/dynamic/' + filename + '_lastday.html')

  #Compute total volunteers on any given data
  active = first_time.append(last_time.rsub(0)).sort_index() #This will give duplicate dates, with the volunteers lost on the date appearing as a negative number after the volunteers gained on the date
  active = active.cumsum() #The final entry for a given date will now be the total volunteers on that date
  dup_mask = active.index.duplicated(keep = 'last') #Identify the duplicates -- last occurence will be marked False, others True (re https://www.kite.com/python/answers/how-to-remove-rows-in-a-pandas-dataframe-with-duplicate-indices-in-python)
  dup_mask = ~dup_mask #Invert the mask so that last entries are True, others False
  active = active[dup_mask]
  full_index = pd.date_range(active.index.min(), '2022-01-31') #Ensure that we have an explicit point for every date (I think it spaces out correctly -- the bar charts above certainly do -- but it is nice to be able to mouseover and see every point)
  active = active.reindex(full_index, method = 'ffill')
  fig = px.line(active, title = f'{label}<br>Volunteers on date', color=px.Constant('Total'))

  #Add the gain as a bar chart
  gain = first_time.subtract(last_time, fill_value = 0)
  fig = fig.add_bar(x = gain.index, y = gain.values, name = 'Gain')

  fig.write_image(filepath + '/static/' + filename + '_gain.svg', width = 1600, height = 1200)
  fig.write_image(filepath + '/static/' + filename + '_gain.png', width = 1600, height = 1200)
  fig.write_html(filepath + '/dynamic/' + filename + '_gain.html')


def start_stop_dates(df, subsets):
  print('Computing first and last classification dates')

  proj_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_times/project/first_last_day/')
  flow_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_times/workflow/first_last_day/')
  type_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_times/workflow_type/first_last_day/')
  for x in 'static', 'dynamic':
    os.makedirs(proj_path + '/' + x)
    os.makedirs(flow_path + '/' + x)
    os.makedirs(type_path + '/' + x)

  procs = []
  #By project
  for project, wids in d.PROJECTS.items():
    print(f'  ... for project {project!r}')
    p = Process(target = drawit, args = (f'All workflows in project <b>{project!r}   {[u.git_condition()]}</b><br>UTC dates', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project)))
    p.start()
    procs.append(p)

  #By workflow
  for workflow, wid in list(zip(d.WORKFLOWS, d.WORKFLOWS.index)):
    print(f'  ... for workflow {workflow!r}')
    p = Process(target = drawit, args = (f'Workflow <b>{workflow}</b>   [{u.git_condition()}]<br>UTC dates', df[df.workflow_id == wid], flow_path, u.fnam_norm(workflow)))
    p.start()
    procs.append(p)

  #By workflow type
  for w_type, wids in d.WORKFLOW_TYPES_BACKMAP.items():
    print(f'  ... for workflow type {w_type!r}')
    p = Process(target = drawit, args = (f'All workflows of type <b>{w_type}</b>   [{u.git_condition()}]<br>UTC dates', df[df.workflow_id.isin(wids)], type_path, u.fnam_norm(w_type)))
    p.start()
    procs.append(p)
  for p in procs: p.join()
