%				%
% Exporing reference data for ALS
%

func_name = 'amp2k';
channel_names = {'Setpoint', 'Monitor'}
currents = 50:10:140;

family_name = 'QFA';
% Still sticking with arrays of chars ... who knows on which MATLAB it needs to run
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents)
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end

family_name = 'QF';

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents)
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


family_name = 'QD';

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents)
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


family_name = 'QDA';

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents)
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end
