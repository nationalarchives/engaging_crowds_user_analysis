import data as d
import util as u
import pandas as pd
import plotly.express as px
import os
from multiprocessing import Process

#Re https://plotly.com/python/marker-style/
#Or import plotly;print(plotly.validators.scatter.marker.SymbolValidator().values)
def SYMBOLS():
  #Figure output seems to go wrong for some orderings of these numbers, and for some symbols
  for x in (0, 5, 3, 1, 18, 25, 2, 17, 20, 4, 22, 21, 26, 27): yield x

def drawit(label, df, filepath, filename):
  first_time = df.groupby('pseudonym')['md.started_at'].min().dt.date
  first_time = first_time.value_counts()
  last_time = df.groupby('pseudonym')['md.finished_at'].max().dt.date
  last_time = last_time.value_counts()

  fig = px.bar(first_time, title = f'{label}<br>Number of volunteers making first classification on date')
  fig.write_image(filepath + '/static/' + filename + '_firstday.svg', width = 1600, height = 1200)
  fig.write_image(filepath + '/static/' + filename + '_firstday.png', width = 1600, height = 1200)
  fig.write_html(filepath + '/dynamic/' + filename + '_firstday.html', include_plotlyjs = 'directory')
  first_time.to_csv(filepath + '/' + filename + '_first_time.csv', mode = 'x')

  fig = px.bar(last_time, title = f'{label}<br>Number of volunteers making final classification on date')
  fig.write_image(filepath + '/static/' + filename + '_lastday.svg', width = 1600, height = 1200)
  fig.write_image(filepath + '/static/' + filename + '_lastday.png', width = 1600, height = 1200)
  fig.write_html(filepath + '/dynamic/' + filename + '_lastday.html', include_plotlyjs = 'directory')
  last_time.to_csv(filepath + '/' + filename + '_last_time.csv', mode = 'x')

  #Compute total volunteers on any given data
  active = first_time.append(last_time.rsub(0)).sort_index() #This will give duplicate dates, with the volunteers lost on the date appearing as a negative number after the volunteers gained on the date
  #There are likely to be some dates with only one entry -- these are dates on which we have only gained or lost volunteers.
  active = active.cumsum() #The final entry for a given date will now be the total volunteers on that date -- this includes the case where there is only 1 entry for a given date
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
  fig.write_html(filepath + '/dynamic/' + filename + '_gain.html', include_plotlyjs = 'directory')
  active.to_csv(filepath + '/' + filename + '_active.csv', mode = 'x')
  gain.to_csv  (filepath + '/' + filename + '_gain.csv', mode = 'x')

  return active

def start_stop_dates(df, subsets):
  SINGLE = True

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
    if SINGLE:
      drawit                              (f'All workflows in project <b>{project!r}   {[u.git_condition()]}</b><br>UTC dates', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project))
    else:
      p = Process(target = drawit, args = (f'All workflows in project <b>{project!r}   {[u.git_condition()]}</b><br>UTC dates', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project)))
      p.start()
      procs.append(p)

  #By workflow
  actives = {}
  for workflow, wid in list(zip(d.WORKFLOWS, d.WORKFLOWS.index)):
    print(f'  ... for workflow {workflow!r} ({d.LABELS[wid]})')
    if wid in actives: raise Exception()
    actives[wid] = drawit(f'Workflow <b>{d.LABELS[wid]}</b>   [{u.git_condition()}]<br>UTC dates', df[df.workflow_id == wid], flow_path, u.fnam_norm(workflow))

  for project, wids in d.PROJECTS.items():
    import plotly.graph_objects as go
    fig = go.Figure(layout = { 'colorway': px.colors.qualitative.Dark24, #re https://plotly.com/python/discrete-color/
                               'template': 'simple_white',
    })
    fig.update_layout(title = f'Active volunteers on {project} {[u.git_condition()]}')
    for wid in wids:
      fig.add_trace(go.Scatter(x = actives[wid].index, y = actives[wid].values, name = d.LABELS[wid]))

    if project == d.HMS: #Special case, as this one is cluttered
      #Line-only
      fig.update_traces(line_width = 4)
      fig.write_image(proj_path + '/static/' + u.fnam_norm(project) + '_agg_gain_line.png', width = 1600, height = 1200)
      fig.write_html(proj_path + '/dynamic/' + u.fnam_norm(project) + '_agg_gain_line.html')

      #Letter-only (experimental)
      import string
      letters = (x for x in string.ascii_uppercase)
      fig.for_each_trace(lambda x: x.update(mode = 'text', text=next(letters)))
      fig.update_traces(textfont_size = 8)
      fig.write_image(proj_path + '/static/' + u.fnam_norm(project) + '_agg_gain_letters.png', width = 1600, height = 1200)
      fig.write_html(proj_path + '/dynamic/' + u.fnam_norm(project) + '_agg_gain_letters.html')

    #Alter the figure to work nicely with symbols, and put the symbols in
    if project == d.HMS: fig.update_traces(mode =       'markers', marker_size = 6) #Big symbols on this one will just smoosh together, lines make it even more cluttered
    else:                fig.update_traces(mode = 'lines+markers', marker_size = 8, line_width = 1, line_dash = 'dot')
    symbols = SYMBOLS()
    fig.for_each_trace(lambda x: x.update(marker_symbol = next(symbols)))
    fig.write_image(proj_path + '/static/' + u.fnam_norm(project) + '_agg_gain.png', width = 1600, height = 1200)
    fig.write_html(proj_path + '/dynamic/' + u.fnam_norm(project) + '_agg_gain.html', include_plotlyjs = 'directory')

    #Data is the same for all of the above figure variations
    pd.Series().append([actives[x] for x in wids]).to_csv(proj_path + '/' + u.fnam_norm(project) + '_agg_gain.csv', mode = 'x')

  special_workflow_map = {
    'Numbers': [18611, 18616, 18619, 18625],
    'Dates': [18612, 18623],
    'Dropdowns': [18614, 18624],
    'Nouns': [18613, 18617, 18618, 18621, 18622],
  }

  for w_type, t_wids in special_workflow_map.items():
    fig = go.Figure(layout = { 'colorway': px.colors.qualitative.Dark24, #re https://plotly.com/python/discrete-color/
                               'template': 'simple_white'
    })
    fig.update_layout(title = f'Active volunteers on HMS NHS ({w_type}) {[u.git_condition()]}')
    for t_wid in t_wids:
      fig.add_trace(go.Scatter(x = actives[t_wid].index, y = actives[t_wid].values, name = d.LABELS[t_wid]))
    fig.update_traces(mode = 'lines+markers', marker_size = 8, line_width = 1, line_dash = 'dot')
    symbols = SYMBOLS()
    fig.for_each_trace(lambda x: x.update(marker_symbol = next(symbols)))
    fig.write_image(type_path + '/static/' + u.fnam_norm(w_type) + '_agg_gain.png', width = 1600, height = 1200)
    fig.write_html(type_path + '/dynamic/' + u.fnam_norm(w_type) + '_agg_gain.html', include_plotlyjs = 'directory')
    pd.Series().append([actives[x] for x in t_wids]).to_csv(type_path + '/' + u.fnam_norm(w_type) + '_agg_gain.csv', mode = 'x')

  #By workflow type
  for w_type, wids in d.WORKFLOW_TYPES_BACKMAP.items():
    print(f'  ... for workflow type {w_type!r}')
    if SINGLE:
      drawit                              (f'All workflows of type <b>{w_type}</b>   [{u.git_condition()}]<br>UTC dates', df[df.workflow_id.isin(wids)], type_path, u.fnam_norm(w_type))
    else:
      p = Process(target = drawit, args = (f'All workflows of type <b>{w_type}</b>   [{u.git_condition()}]<br>UTC dates', df[df.workflow_id.isin(wids)], type_path, u.fnam_norm(w_type)))
      p.start()
      procs.append(p)
  if not SINGLE:
    for p in procs: p.join()
