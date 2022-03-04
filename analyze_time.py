#!/usr/bin/env python3

import data as d
import util as u

import pandas as pd
import plotly.io as pio
import plotly.express as px

import os
from multiprocessing import Process

def durations(durations_df, subsets):
  durations_df.duration = durations_df.duration.dt.total_seconds().div(60)
  filepath = f'secrets/graphs/{d.HEAD}/class_times/workflow/duration_stats'
  for x in 'static', 'dynamic': os.makedirs(filepath + '/' + x)
  fig = px.box(durations_df, x = 'workflow_name', y = 'duration',
               points = 'suspectedoutliers', notched = True,
               labels = { 'workflow_name': 'Workflow Name', 'duration': 'Minutes'})
  fig.update_traces(quartilemethod = 'linear')
  fig.write_image(filepath + '/static/all_times_box.svg', width = 1600, height = 1200)
  fig.write_image(filepath + '/static/all_times_box.png', width = 1600, height = 1200)
  fig.write_html(filepath + '/dynamic/all_times_box.html')
  durations_df.to_csv(filepath + '/all_times_box.csv', mode = 'x')
  print('\nStatistical overview of workflow durations')
  print('=' * len('Statistical overview of workflow durations'))
  for project, wids in d.PROJECTS.items():
    print('\n' + project); print('-' * len(project))
    print(pd.DataFrame(
      { d.LABELS[wid]: durations_df[durations_df.workflow_id == wid]['duration'] for wid in wids }
    ).describe())


def start_times(start_df, subsets):
  SINGLE = True

  print('Computing all times started (local time)')

  def convert_period(x):
    if x.hour >=  0 and x.hour <  4: return 0
    if x.hour >=  4 and x.hour <  8: return 1
    if x.hour >=  8 and x.hour < 12: return 2
    if x.hour >= 12 and x.hour < 16: return 3
    if x.hour >= 16 and x.hour < 20: return 4
    if x.hour >= 20 and x.hour < 24: return 5
    assert False

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
    volunteer_classification_counts = data.pseudonym.value_counts()
    n_v = len(volunteer_classification_counts)
    n_class = len(data)

    if kwargs.get('box'):
      logfile = open(filepath + '/' + filename + '_desc.txt', 'x')
      title = f'{label} ({n_v} volunteers)   [{u.git_condition()}]'
      print(title, file = logfile)
      description = volunteer_classification_counts.describe([0.25, 0.75, 0.9, 0.95, 0.99])
      q1 = description['25%']
      q3 = description['75%']
      iqr = q3 - q1
      upper_fence = q3 + iqr * 1.5
      upper_outer_fence = q3 + iqr * 3
      lower_fence = q1 - iqr * 1.5
      lower_inner_fence = q1 - iqr * 3
      print('count:', description['count'], file = logfile)
      print('std:  ', description['std'], file = logfile)
      print('< / == / >', file = logfile)
      description = description.append(pd.Series({
        'mean +  \u03C3': description['mean'] + description['std'],
        'mean + 2\u03C3': description['mean'] + 2 * description['std'],
        'upper fence': upper_fence,
        'upper outer fence': upper_outer_fence,
      }))
      for k, v in description.iteritems():
        if k == 'count' or k == 'std': continue
        lt = len(volunteer_classification_counts[volunteer_classification_counts.lt(v)])
        eq = len(volunteer_classification_counts[volunteer_classification_counts.eq(v)])
        gt = len(volunteer_classification_counts[volunteer_classification_counts.gt(v)])
        assert lt + eq + gt == n_v
        p_lt = lt / n_v
        p_eq = eq / n_v
        p_gt = gt / n_v
        print(f'{k+":":20} {v:7.02f} classifications, {lt:7}/{eq:7}/{gt:7} volunteers ({p_lt:03.02%}/{p_eq:03.02%}/{p_gt:03.02%} of all volunteers)', file = logfile)
      logfile.close()

      description = str(description)
      description = description[:description.rfind('\n')].replace('\n', '<br>')
      title += '<br>' + description

      #Show the spread of volunteer classification counts
      volunteer_classification_counts.to_csv(filepath + '/' + filename + '_box.csv', mode = 'x')
      fig = px.box(volunteer_classification_counts, #x = 'workflow_name', y = session_df.duration.apply(lambda x: x.ceil('T').total_seconds()/60),
                   points = 'suspectedoutliers', notched = True,
                   title = title, labels = { 'y': 'Classifications', 'x': ''}, log_y = True)
      fig.update_traces(quartilemethod = 'linear')
      fig.write_image(filepath + '/static/' + filename + '_box.svg', width = 1600, height = 1200)
      fig.write_image(filepath + '/static/' + filename + '_box.png', width = 1600, height = 1200)
      fig.write_html(filepath + '/dynamic/' + filename + '_box.html')

      #Dump the heatmaps as cut by q3
      #TODO All lot of this should very much be factored out to some subroutine
      q1_pseudonyms   = volunteer_classification_counts[volunteer_classification_counts.le(q1)].index.copy().values
      low_pseudonyms  = volunteer_classification_counts[volunteer_classification_counts.le(q3)].index.copy().values
      high_pseudonyms = volunteer_classification_counts[volunteer_classification_counts.gt(q3)].index.copy().values
      title = f'{label} per weekday and period, in local time  [{u.git_condition()}]'
      title += f'<br>Volunteers <= 3rd quartile classifications ({len(low_pseudonyms)} volunteers doing up to {int(q3)} classifications) ({len(data[data.pseudonym.isin(low_pseudonyms)])} total classifications)'
      fig = px.density_heatmap(data[data.pseudonym.isin(low_pseudonyms)], x = 'day', y = 'period',
                               histnorm = 'percent', histfunc = 'count',
                               marginal_x = 'histogram', marginal_y = 'histogram',
                               title = title,
                               category_orders = {'day': DAYS, 'period': PERIODS})
      fig.write_image(filepath + '/static/' + filename + '_q3.svg', width = 1600, height = 1200)
      fig.write_image(filepath + '/static/' + filename + '_q3.png', width = 1600, height = 1200)
      fig.write_html(filepath + '/dynamic/' + filename + '_q3.html')
      data[data.pseudonym.isin(low_pseudonyms)].to_csv(filepath + '/' + filename + '_q3.csv', mode = 'x')

      title = f'{label} per weekday and period, in local time  [{u.git_condition()}]'
      title += f'<br>Volunteers > 3rd quartile classifications ({len(high_pseudonyms)} volunteers doing over {int(q3)} classifications ({volunteer_classification_counts.loc[high_pseudonyms].min()} to {volunteer_classification_counts.loc[high_pseudonyms].max()} classifications)) ({len(data[data.pseudonym.isin(high_pseudonyms)])} total classifications)'
      fig = px.density_heatmap(data[data.pseudonym.isin(high_pseudonyms)], x = 'day', y = 'period',
                               histnorm = 'percent', histfunc = 'count',
                               marginal_x = 'histogram', marginal_y = 'histogram',
                               title = title,
                               category_orders = {'day': DAYS, 'period': PERIODS})
      fig.write_image(filepath + '/static/' + filename + '_q4.svg', width = 1600, height = 1200)
      fig.write_image(filepath + '/static/' + filename + '_q4.png', width = 1600, height = 1200)
      fig.write_html(filepath + '/dynamic/' + filename + '_q4.html')
      data[data.pseudonym.isin(high_pseudonyms)].to_csv(filepath + '/' + filename + '_q4.csv', mode = 'x')

      title = f'{label} per weekday and period, in local time  [{u.git_condition()}]'
      title += f'<br>Volunteers <= 1st quartile classifications ({len(q1_pseudonyms)} volunteers doing up to {int(q1)} classifications) ({len(data[data.pseudonym.isin(q1_pseudonyms)])} total classifications)'
      fig = px.density_heatmap(data[data.pseudonym.isin(q1_pseudonyms)], x = 'day', y = 'period',
                               histnorm = 'percent', histfunc = 'count',
                               marginal_x = 'histogram', marginal_y = 'histogram',
                               title = title,
                               category_orders = {'day': DAYS, 'period': PERIODS})
      fig.write_image(filepath + '/static/' + filename + '_q1.svg', width = 1600, height = 1200)
      fig.write_image(filepath + '/static/' + filename + '_q1.png', width = 1600, height = 1200)
      fig.write_html(filepath + '/dynamic/' + filename + '_q1.html')
      data[data.pseudonym.isin(q1_pseudonyms)].to_csv(filepath + '/' + filename + '_q1.csv', mode = 'x')

      for iteration in range(1, 5):
        random_pseudonyms = data.sample(frac = 0.25)
        title = f'{label} per weekday and period, in local time  [{u.git_condition()}]'
        title += f'<br>Random 25% of all {n_class} classifications)'
        fig = px.density_heatmap(random_pseudonyms, x = 'day', y = 'period',
                                 histnorm = 'percent', histfunc = 'count',
                                 marginal_x = 'histogram', marginal_y = 'histogram',
                                 title = title,
                                 category_orders = {'day': DAYS, 'period': PERIODS})
        fig.write_image(filepath + '/static/' + filename + f'_r{iteration}.svg', width = 1600, height = 1200)
        fig.write_image(filepath + '/static/' + filename + f'_r{iteration}.png', width = 1600, height = 1200)
        fig.write_html(filepath + '/dynamic/' + filename + f'_r{iteration}.html')
        random_pseudonyms.to_csv(filepath + '/' + filename + f'_r{iteration}.csv', mode = 'x')

    #Compute the heatmaps of when classifications happened
    title = f'{label} per weekday and period, in local time ({n_v} volunteers)  [{u.git_condition()}]'
    if n_v != n_class:
        mean_v = volunteer_classification_counts.mean()
        std_v = volunteer_classification_counts.std()
        med_v = volunteer_classification_counts.median()
        title += f'<br>{n_class} classifications ({n_v} volunteers, {n_class} classifications, median = {med_v}, mean = {mean_v:.2f} (\u03C3 = {std_v:.2f}))'

    fig = px.density_heatmap(data, x = 'day', y = 'period',
                              histnorm = 'percent', histfunc = 'count',
                              marginal_x = 'histogram', marginal_y = 'histogram',
                              title = title,
                              category_orders = {'day': DAYS, 'period': PERIODS})
    #pio.show(fig, renderer = 'browser')
    fig.write_image(filepath + '/static/' + filename + '.svg', width = 1600, height = 1200)
    fig.write_image(filepath + '/static/' + filename + '.png', width = 1600, height = 1200)
    fig.write_html(filepath + '/dynamic/' + filename + '.html')

    #Record the data used to make these graphs
    data.to_csv(filepath + '/' + filename + '.csv', mode = 'x')

  procs = []
  for label, df, box in [('all classifiers', start_df, True)]:
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
      if SINGLE:
        drawit                              (f'{title}<br>All workflows in project <b>{project!r}</b>', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project),             box = box)
      else:
        p = Process(target = drawit, args = (f'{title}<br>All workflows in project <b>{project!r}</b>', df[df.workflow_id.isin(wids)], proj_path, u.fnam_norm(project)), kwargs = {'box': box})
        p.start()
        procs.append(p)

    #By workflow
    for workflow, wid in list(zip(d.WORKFLOWS, d.WORKFLOWS.index)):
      print(f'  ... for workflow {workflow!r} ({d.LABELS[wid]})')
      if SINGLE:
        drawit                              (f'{title}<br>Workflow <b>{d.LABELS[wid]}</b>', df[df.workflow_id == wid], flow_path, u.fnam_norm(workflow),             box = box)
      else:
        p = Process(target = drawit, args = (f'{title}<br>Workflow <b>{d.LABELS[wid]}</b>', df[df.workflow_id == wid], flow_path, u.fnam_norm(workflow)), kwargs = {'box': box})
        p.start()
        procs.append(p)
    
    #By workflow type
    for w_type, wids in d.WORKFLOW_TYPES_BACKMAP.items():
      print(f'  ... for workflow type {w_type!r}')
      if SINGLE:
        drawit                              (f'{title}<br>All workflows of type <b>{w_type}</b>', df[df.workflow_id.isin(wids)], type_path, u.fnam_norm(w_type),             box = box)
      else:
        p = Process(target = drawit, args = (f'{title}<br>All workflows of type <b>{w_type}</b>', df[df.workflow_id.isin(wids)], type_path, u.fnam_norm(w_type)), kwargs = {'box': box})
        p.start()
        procs.append(p)
  if not SINGLE:
    for p in procs: p.join()
