import datetime
from pandas import DataFrame
from pandas import concat


# This function is used to get dates of reddit funcitons
def get_date(submission):
	time = submission.created
	return datetime.datetime.fromtimestamp(time)


# Im[ur a list of dictionaries or just one
def indataframe(dictionary):
	list_of_df = []
	if len(dictionary) > 1:
		for i in range(len(dictionary)):
			df = DataFrame.from_dict(dictionary[i],orient='index')
			df = df.transpose()
			list_of_df.append(df)
		return list_of_df
	else:
		df = DataFrame.from_dict(dictionary)
		return df


# For merging a list of dataframes
def merging(dataframelist):
	dataframe = concat(dataframelist,axis=1)
	return dataframe