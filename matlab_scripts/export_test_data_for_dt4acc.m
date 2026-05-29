%				%
% Exporing reference data for ALS
%

AO  = getao();

channel_names = {'Monitor'};
func_name = 'hw2physics'
positions = -1:.1:1;

% ----------------------------------------
% BPM's
family_name = 'BPMx'
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, positions);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end

family_name = 'BPMy'
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, positions);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


func_name = 'physics2hw'
positions = -1e-3:.5e-4:1e-3;
family_name = 'BPMx'
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, positions);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end

family_name = 'BPMy'
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, positions);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


% ----------------------------------------
% correctors

func_name = 'k2amp';
channel_names = {'Setpoint', 'Monitor'};

% currents for correctors ... just guessing
% code shows that these use linear conversion
angles = -1.5e-3:.5e-4:1.5e-3;
family_name = 'HCM';
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, angles);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end

family_name = 'VCM';
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, angles);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


func_name = 'amp2k';
channel_names = {'Setpoint', 'Monitor'};
currents = -2:.5:2;

family_name = 'HCM';
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end

family_name = 'VCM';
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


% ----------------------------------------
% quadrupoles


func_name = 'k2amp';
channel_names = {'Setpoint', 'Monitor'};



% k_values for quadrupoles

family_name = 'QFA';
k_values = 2.5:.1:3.3;
% Still sticking with arrays of chars ... who knows on which MATLAB it needs to run
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, k_values);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end

family_name = 'QF';
k_values = 1.3:.1:2.4;

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, k_values);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


family_name = 'QD';
k_values = -2.7:.1:-2.0;

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, k_values);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


family_name = 'QDA';
k_values = -0.4:.01:-0.3;

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, k_values);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


func_name = 'amp2k';
channel_names = {'Setpoint', 'Monitor'};


% currents for quadrupoles
currents = 380:10:540;

family_name = 'QFA';
% Still sticking with arrays of chars ... who knows on which MATLAB it needs to run
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end

family_name = 'QF';
currents = 70:5:100;

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


family_name = 'QD';
currents = 80:5:115;

for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end


family_name = 'QDA';
currents = 15:5:65;
for i = 1:length(channel_names)
  channel_name = channel_names{i};

  device_list = AO.(family_name).DeviceList;

  [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, currents);
  json_text = jsonencode(reference_curves_for_family, 'PrettyPrint', true);

  filename = sprintf('reference_test_data_%s_%s_%s.json', family_name, func_name, channel_name);
  fid = fopen(filename, 'w');
  fprintf(fid, '%s', json_text);
  fclose(fid);
end
