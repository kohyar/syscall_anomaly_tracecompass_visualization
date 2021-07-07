################################################################################
# Copyright (c) 2021 Iman Kohyarnejadfard
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# anomaly_detection_visualization.py
################################################################################

# load proper Trace Compass modules
loadModule('/TraceCompass/Analysis');
loadModule('/TraceCompass/View');
loadModule('/TraceCompass/DataProvider');
# Modules
loadModule("/TraceCompass/Trace")
loadModule("/System/Resources")
loadModule("/System/Scripting")
import json

# Get the active trace
trace = getActiveTrace()
if trace is None:
	print("There is no active trace. Please open the trace to run this script on")
	exit()

# Create an analysis named userv_msg_seq.py
analysis = createScriptedAnalysis(getActiveTrace(), "userv_msg_seq_split_j.py")

# Get the analysis's state system so we can fill it, true indicates to re-use an existing state system, false would create a new state system even if one already exists
ss = analysis.getStateSystem(False)

# The state system methods require a vararg array. This puts the string in a vararg array to call those methods
def strToVarargs(str):
    object_class = java.lang.String
    object_array = gateway.new_array(object_class, 1)
    object_array[0] = str
    return object_array

def runAnalysis():
	mapInitialInfo = java.util.HashMap()
	iter = getEventIterator(trace)
	event = None
	cnt = 0
	while iter.hasNext():
		cnt+=1
		#if cnt>100000:
		#	print('break')
		#	break
		event = iter.next();
		cat = getEventFieldValue(event, "cat")
		if cat=='normal':
			quark = ss.getQuarkAbsoluteAndAdd(strToVarargs(str('Execution status')))
			ss.modifyAttribute(event.getTimestamp().toNanos(), 'normal', quark)
		else:
			quark = ss.getQuarkAbsoluteAndAdd(strToVarargs(str('Execution status')))
			ss.modifyAttribute(event.getTimestamp().toNanos(), 'abnormal', quark)
				
	
	# Done parsing the events, close the state system at the time of the last event, it needs to be done manually otherwise the state system will still be waiting for values and will not be considered finished building
	if not(event is None):
		ss.closeHistory(event.getTimestamp().toNanos())
	
			
# This condition verifies if the state system is completed. For instance, if it had been built in a previous run of the script, it wouldn't run again.
if not(ss.waitUntilBuilt(0)):
    # State system not built, run the analysis
    runAnalysis()
  
# Get a time graph provider from this analysis, displaying all attributes (which are the cpus here)
provider = createTimeGraphProvider(analysis, {ENTRY_PATH : '*'});
if not(provider is None):
    # Open a time graph view displaying this provider
    openTimeGraphView(provider)
