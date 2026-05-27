function [reference_curves_for_family] = produce_test_data(func_name, family_name, channel_name, indeps)

% produce_test_data: produce test data for amp2k
  reference_function_name = func_name;

  if exist(reference_function_name, 'file') ~= 2
    error('Function %s not found', reference_function_name);
  end

  func = str2func(func_name);

  % get the ao object
  AO = getao();

  device_list = AO.(family_name).DeviceList;


  all_curves = struct( ...
		       'curve', {}, ...
		       'device_id', {}, ...
		       'channel_name', {}, ...
		       'pv_name', {}, ...
		       'reference_function_name', {} );

  for i = 1:size(device_list, 1)

    dev_index = device_list(i, :);
    pv_name = AO.(family_name).(channel_name).ChannelNames(i, :);
    curve = struct('indep', {}, 'dep', {});

    for j = 1:numel(indeps)
      indep = indeps(j);
      dep = func(family_name, channel_name, indep, dev_index);
        curve(j).indep = indep;
        curve(j).dep   = dep;
    end

    reference_curve = struct();
    reference_curve.curve = curve;
    reference_curve.device_id = struct( ...
        'family', family_name, ...
        'sector', dev_index(1), ...
        'child',  dev_index(2));
    reference_curve.channel_name = channel_name;
    reference_curve.pv_name = pv_name;
    reference_curve.reference_function_name = ...
        reference_function_name;

    all_curves(i) = reference_curve;
end

reference_curves_for_family = struct();
reference_curves_for_family.curves = all_curves;
