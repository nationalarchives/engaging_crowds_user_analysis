import data as d
import util as u
import pandas as pd
import plotly.express as px
import os
from multiprocessing import Process

def drawit(label, df, filepath, filename):
  cpv = df.pseudonym.value_counts(normalize = True).reset_index(drop = True) #% of total classifications per volunteer
  cpv *= 100
  v_c = len(cpv) #volunteer count
  bin_divisor = 20 # i.e. 1/20th
  bin_size = int(v_c / bin_divisor) #size of a division of 1 bin_divisor_th of cpv (rounded down)

  TRUSTING_SO = False

  if TRUSTING_SO:
    #The following line is derived from https://stackoverflow.com/q/47239332.
    #It appears to work but I find it puzzling
    cpv = cpv.groupby(cpv.index // bin_size).sum() #This appears to work, but I don't understand it well enough

    binned_index = [f'{x}th {bin_size} volunteers' for x in range(1, int(v_c / bin_size) + 1)]
    leftovers = v_c % bin_size
    if leftovers != 0:
      binned_index += [f'Final {leftovers} volunteers']
    cpv.index = binned_index
  else:
    binned = []
    i = 1
    while i * bin_size <= v_c:
      end = i * bin_size
      start = end - bin_size
      binned.append(cpv.iloc[start:end].sum())
      i += 1
    binned_index = [f'{x}th {bin_size} volunteers' for x in range(1, i)]
    leftovers = v_c - (i - 1) * bin_size
    assert leftovers >= 0
    assert leftovers < bin_size
    if leftovers != 0:
      binned.append(cpv.iloc[(i - 1) * bin_size:].sum())
      binned_index += [f'Final {leftovers} volunteers']
    cpv = pd.Series(binned, binned_index)


  fig = px.bar(cpv, title = f'{label}<br>% of total classifications by each {bin_size} volunteers, from most to least prolific<br>({len(df)} total classifications by {v_c} total volunteers)', range_y = [0, 100])
  fig.write_image(filepath + '/static/' + filename + '_class_vol.svg', width = 1600, height = 1200)
  fig.write_image(filepath + '/static/' + filename + '_class_vol.png', width = 1600, height = 1200)
  fig.write_html(filepath + '/dynamic/' + filename + '_class_vol.html', include_plotlyjs = 'directory')
  cpv.to_csv  (filepath + '/' + filename + '_class_vol.csv', mode = 'x')



def classifications(df, subsets):
  SINGLE = True

  print('Computing volunteers per classification count')

  proj_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_counts/project/')
  flow_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_counts/workflow/')
  type_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_counts/workflow_type/')
  for x in 'static', 'dynamic':
    os.makedirs(proj_path + '/' + x)
    os.makedirs(flow_path + '/' + x)
    os.makedirs(type_path + '/' + x)

  procs = []
  #By project
  for project, wids in d.PROJECTS.items():
    print(f'  ... for project {project!r}')
    if SINGLE:
      drawit                              (f'All workflows in project <b>{project!r}   {[u.git_condition()]}</b>', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project))
    else:
      p = Process(target = drawit, args = (f'All workflows in project <b>{project!r}   {[u.git_condition()]}</b>', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project)))
      p.start()
      procs.append(p)

  #By workflow
  for workflow, wid in list(zip(d.WORKFLOWS, d.WORKFLOWS.index)):
    print(f'  ... for workflow {workflow!r} ({d.LABELS[wid]})')
    if SINGLE:
      drawit                              (f'Workflow <b>{d.LABELS[wid]}</b>   [{u.git_condition()}]', df[df.workflow_id == wid], flow_path, u.fnam_norm(workflow))
    else:
      p = Process(target = drawit, args = (f'Workflow <b>{d.LABELS[wid]}</b>   [{u.git_condition()}]', df[df.workflow_id == wid], flow_path, u.fnam_norm(workflow)))
      p.start()
      procs.append(p)

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
