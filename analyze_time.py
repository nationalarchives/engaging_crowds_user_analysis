#!/usr/bin/env python3

import data as d
import util as u

import pandas as pd
import plotly.io as pio
import plotly.express as px

import os

def start_times(start_df, subsets):

  print('Computing all times started (local time)')

  def convert_period(x):
    if x.hour >=  0 and x.hour <  4: return 0
    if x.hour >=  4 and x.hour <  8: return 1
    if x.hour >=  8 and x.hour < 12: return 2
    if x.hour >= 12 and x.hour < 16: return 3
    if x.hour >= 16 and x.hour < 20: return 4
    return 5

    #Alternative periods -- uneven, harder to think about
    if x.hour >= 0 and x.hour < 6:  return 0 #very early morning
    if x.hour >= 6 and x.hour < 9:  return 1 #early morning
    if x.hour >= 9 and x.hour < 12: return 2 #morning
    if x.hour >=12 and x.hour < 14: return 3 #lunchtime
    if x.hour >=14 and x.hour < 18: return 4 #afternoon
    if x.hour >=18 and x.hour < 21: return 5 #evening
    return 6 #night

  def convert_day(x):
    assert (x.weekday() >= 0 and x.weekday() <= 6)
    return x.weekday()

  DAYS = ['Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', 'Sun']
  PERIODS = ['Small hours', 'Early morning', 'Morning', 'Afternoon', 'Evening', 'Night']

  start_df['period'] = start_df['local.started_at'].apply(convert_period)
  start_df['day'] = start_df['local.started_at'].apply(convert_day)
  start_df = start_df[['project', 'pseudonym', 'workflow_id', 'workflow_name', 'day', 'period']].sort_values(['day', 'period'])
  start_df.day = start_df.day.map(dict(enumerate(DAYS))) #Re https://stackoverflow.com/a/48472623
  start_df.period = start_df.period.map(dict(enumerate(PERIODS)))
  PERIODS.reverse() #for the heatmap drawing

  print('Sample from start times table')
  print(start_df.sample(5))

  #Now do the drawing

  def drawit(label, data, filepath, filename, **kwargs):
    #If I understand correctly, it doesn't matter what 'z' is here, as I am just counting the cells where day and hour intersect
    #As a result, I am displaying the bar chart of classifications per day at the top (marginal_x) and the bar chart of
    #classifications per period on the right (marginal_y).
    #I've checked this with the default Workflows and Period, and the values seem to be correct, so I probably do
    #understand correctly.
    volunteer_classification_counts = data.pseudonym.value_counts()
    n_v = len(volunteer_classification_counts)
    n_class = len(data)

    if kwargs.get('box'):
      description = volunteer_classification_counts.describe([0.25, 0.75, 0.9, 0.95, 0.99])
      q1 = description['25%']
      q3 = description['75%']
      iqr = q3 - q1
      upper_fence = q3 + iqr * 1.5
      upper_outer_fence = q3 + iqr * 3
      lower_fence = q1 - iqr * 1.5
      lower_inner_fence = q1 - iqr * 3

      description = str(description)
      description = description[:description.rfind('\n')]
      description += f'Upper outer fence: {upper_outer_fence}\nUpper fence: {upper_fence}\nLower fence: {lower_fence}\nLower inner fence: {lower_inner_fence}'
      title = f'{label} ({n_v} volunteers)'
      print(title)
      print(description)
      title += '<br>' + description.replace('\n', '<br>')

      #Show the spread of volunteer classification counts
      fig = px.box(volunteer_classification_counts, #x = 'workflow_name', y = session_df.duration.apply(lambda x: x.ceil('T').total_seconds()/60),
                   points = 'suspectedoutliers', notched = True,
                   title = title, labels = { 'y': 'Classifications', 'x': ''}, log_y = True)
      fig.update_traces(quartilemethod = 'linear')
      fig.write_image(filepath + '/static/' + filename + '_box.svg', width = 1600, height = 1200)
      fig.write_html(filepath + '/dynamic/' + filename + '_box.html')

    title = f'{label} per weekday and period, in local time ({n_v} volunteers)  [{u.git_condition()}]'
    if n_v != n_class:
        mean_v = volunteer_classification_counts.mean()
        std_v = volunteer_classification_counts.std()
        med_v = volunteer_classification_counts.median()
        title += f'<br>{n_class} classifications ({n_v} volunteers, {n_class} classifications, median = {med_v}, mean = {mean_v:.2f} (\u03C3 = {std_v:.2f}))'

    #Compute the heatmaps of when classifications happened
    fig = px.density_heatmap(data, x = 'day', y = 'period', z = 'project',
                              histnorm = 'percent', histfunc = 'count',
                              marginal_x = 'histogram', marginal_y = 'histogram',
                              title = title,
                              category_orders = {'day': DAYS, 'period': PERIODS})
    #pio.show(fig, renderer = 'browser')
    fig.write_image(filepath + '/static/' + filename + '.svg', width = 1600, height = 1200)
    fig.write_html(filepath + '/dynamic/' + filename + '.html')

    #Record the data used to make these graphs
    data.to_csv(filepath + '/' + filename + '.csv')

  for label, df, box in ('all classifiers', start_df, True), \
                        ('mono classifiers', start_df.loc[subsets['mono']], False), \
                        ('multi classifiers', start_df.loc[subsets['plural']], False):
    proj_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_times/project/{label}')
    flow_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_times/workflow/{label}')
    type_path = u.path_norm(f'secrets/graphs/{d.HEAD}/class_times/workflow_type/{label}')
    for x in 'static', 'dynamic':
      os.makedirs(proj_path + '/' + x)
      os.makedirs(flow_path + '/' + x)
      os.makedirs(type_path + '/' + x)
    
    title = f'Classifications by {label}  [{u.git_condition()}]'
    print(f'Drawing {title}...')

    #By project
    for project, wids in d.PROJECTS.items():
      print(f'  ... for project {project!r}')
      drawit(f'{title}<br>All workflows in project <b>{project!r}</b>', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project), box = box)

    #By workflow
    for workflow, wid in list(zip(d.WORKFLOWS, d.WORKFLOWS.index)):
      print(f'  ... for workflow {workflow!r}')
      drawit(f'{title}<br>Workflow <b>{workflow}</b>', df[df.workflow_id == wid], flow_path, u.fnam_norm(workflow), box = box)
    
    #By workflow type
    for w_type, wids in d.WORKFLOW_TYPES_BACKMAP.items():
      print(f'  ... for workflow type {w_type!r}')
      drawit(f'{title}<br>All workflows of type <b>{w_type}</b>', df[df.workflow_id.isin(wids)], type_path, u.fnam_norm(w_type), box = box)
