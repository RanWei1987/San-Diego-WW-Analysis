import sys
# replace with freyja path
sys.path.append(r"C:\Users\E107484\Documents\projects\Freyja")
from freyja.utils import prepLineageDict
import copy
import pandas as pd
# below supresses SettingWithCopyWarning
pd.options.mode.chained_assignment = None
from datetime import date,timedelta,datetime
import yaml
# import sys
# # replace with freyja path
# sys.path.insert(1, '/shared/workspace/software/freyja')



with open("plot_config.yml", "r" ) as f :
    plot_config = yaml.safe_load(f)
#make copy of config for later
plot_config_ = copy.deepcopy(plot_config)
#remove the "Recombinants" and "Other" keys for now.
del plot_config['Other']
del plot_config['Recombinants']
for key in reversed( list( plot_config.keys() ) ):
    plot_config[key]['members'] = [mem.replace('.X','*') for mem in plot_config[key]['members']]
   #----#
# update the file below with the update freyja command
with open('lineages.yml', 'r') as f:
        try:
            lineages_yml = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise ValueError('Error in lineages.yml file: ' + str(exc))
lineage_info = {}
for lineage in lineages_yml:
    lineage_info[lineage['name']] = {'children': lineage['children']}
agg_df = pd.read_csv(f'agg_outputs.tsv', skipinitialspace=True, sep='\t',index_col=0)
agg_df = agg_df[agg_df['coverage'] > 60]
agg_df = prepLineageDict(agg_df,thresh=0.0000000001,config=plot_config,lineage_info=lineage_info)
formatted_agg = agg_df['linDict'].apply(pd.Series)
# drop any columns that aren't in the plot_config file
# formatted_agg = formatted_agg[[key for key in plot_config_.keys() if key in formatted_agg.columns]]
#add abundance associated with things not in the plot config to recombinants or other
recombs = [fc for fc in formatted_agg.columns if (fc not in plot_config.keys()) and (fc[0]=='X')]
# formatted_agg['Recombinants'] = formatted_agg[recombs].sum(axis=1)
# The conditions [key for key in plot_config_.keys() if key in formatted_agg.columns] and [fc for fc in formatted_agg.columns if (fc not in plot_config.keys()) and (fc[0]=='X')] are in conflict. So, for new samples, the column Recombinants are left 0
formatted_agg['Recombinants'] = 0
# formatted_agg = formatted_agg.drop(columns=recombs)
# Column selection is cancelled at this stage as the output will cluster lineages into major categories
# Plus, according to the graph, "Other" is actually calculated by 1 - sum(all major category ratios), so the calculation procedure is deprecated
# others = [fc for fc in formatted_agg.columns if (fc not in plot_config.keys()) and fc!='Recombinants']
# Reverse engineered definition on how UCSD processed the dataframe for output
# formatted_agg['Other'] = 1 - formatted_agg.sum(axis=1)
# Remove possible < 0 values due to roundup operations
# formatted_agg['Other'] = formatted_agg['Other'].where(abs(formatted_agg['Other']) > 0.4, 0)
#formatted_agg = formatted_agg.drop(columns=others)
# drop any columns that aren't in the plot_config file
formatted_agg = formatted_agg[[key for key in plot_config_.keys() if key in formatted_agg.columns]]
formatted_agg = formatted_agg.mul(100)
#separate out by site
pl_agg = formatted_agg[formatted_agg.index.str.contains('PL')]
enc_agg = formatted_agg[(formatted_agg.index.str.contains('ENC')) | (formatted_agg.index.str.contains('EN-'))]
sb_agg = formatted_agg[formatted_agg.index.str.contains('SB')]
pl_agg = pl_agg.reset_index()
enc_agg = enc_agg.reset_index()
sb_agg = sb_agg.reset_index()

lookup = pd.read_csv('all-ww-metadata-UCSD.csv').drop_duplicates(keep='first')
lookup = lookup.set_index('sample_name')
lookup['collection_date'] = pd.to_datetime(lookup['collection_date'])


def add_date_and_site_to_agg(agg_df, lookup):
    records_old_index = agg_df.index[agg_df['index'].str.contains('__')]
    records_new_index = agg_df.index[agg_df['index'].str.contains('WW0')]

    keys_old = agg_df.loc[records_old_index, 'index'].str.split('__').str[0]
    keys_new = agg_df.loc[records_new_index, 'index'].str.split('_freyja_demixed').str[0]
    print("The following entries are included multiple times:", keys_old[keys_old.duplicated()])
    print("The following lookups are included multiple times:", lookup.index[lookup.index.duplicated()])
    agg_df.loc[records_old_index, 'collection_date'] = keys_old.map(lookup['collection_date'])
    agg_df.loc[records_new_index, 'collection_date'] = "20"+keys_new.str.extract(r'(?:PL|EN|SB)-(\d{2}-\d{2}-\d{2})')[0]
 
    # print("Following rows were dropped because index was not in all-ww-metadata-UCSD.csv")
    # print("\n".join(agg_df[agg_df['collection_date'].isna()]['index'].tolist()))
    # print("\n")
    agg_df.dropna(subset=['collection_date'], inplace=True)
    agg_df.drop(columns=['index'], inplace=True)
    agg_df = agg_df.loc[agg_df['collection_date'] >= pd.to_datetime('2021-01-01')]

for agg_df in [pl_agg, enc_agg, sb_agg]:
    add_date_and_site_to_agg(agg_df, lookup)

pl_agg = pl_agg.rename(columns={"collection_date": "Date"})
enc_agg = enc_agg.rename(columns={"collection_date": "Date"})
sb_agg = sb_agg.rename(columns={"collection_date": "Date"})
# pull the latest summary files from github and read as df
# https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/PointLoma_sewage_seqs.csv
# https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/Encina_sewage_seqs.csv
# https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/SouthBay_sewage_seqs.csv
pl_agg['Date'] = pd.to_datetime(pl_agg['Date'], format='%Y-%m-%d')
pl_git_df = pd.read_csv("https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/PointLoma_sewage_seqs.csv")

# pl_git_df = pl_git_df.drop(pl_git_df.tail(16).index)
pl_git_df['Date'] = pd.to_datetime(pl_git_df['Date'])
# pl_git_df = pl_git_df[pl_git_df['Date']<=pl_agg['Date'].min()] # allow changes in parameters to impact the outputs
pl_out_df = pd.concat([pl_git_df, pl_agg])
# pl_out_df = pl_out_df[['Date', 'BA.1', 'BA.1.1.X', 'BA.2.X', 'BA.2.12.X', 'BA.4.X', 'BA.5.X', 'B.1.1.529', 'AY.113', 'AY.100', 'AY.20', 'AY.25', 'AY.3', 'AY.44', 'AY.119', 'AY.3.1', 'AY.103', 'AY.46.4', 'AY.25.1', 'AY.116', 'AY.43.4', 'Other Delta sub-lineages','BA.2.75', 'BA.4.6', 'BQ.1.X', 'BQ.1.1.X', 'BF.7.X','BN.1.X', 'XBB.X', 'XBB.1.5.X', 'XBB.1.9.X', 'XBB.1.16.X', 'XBB.2.3.X', 'EG.5.X', 'BA.2.86.X', 'HV.1.X', 'JN.1.X', 'JN.1.7.X', 'JN.1.4.X', 'KQ.1.X', 'JN.1.11.X', 'KP.2.X', 'Recombinants', 'Other']]
pl_out_df = pl_out_df.fillna(0.00).round(2).drop_duplicates(subset=['Date'],keep='first')
pl_out_df = pl_out_df.sort_values(by=['Date'])
pl_out_df["Site"] = "Point Loma"
# pl_out_df.to_csv('PointLoma_sewage_seqs.csv', index=False)
# pl_out_df.to_csv('freyja_reports/output/PointLoma_sewage_seqs.csv')
enc_agg['Date'] = pd.to_datetime(enc_agg['Date'], format='%Y-%m-%d')
enc_git_df = pd.read_csv("https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/Encina_sewage_seqs.csv")
# enc_git_df = enc_git_df.drop(enc_git_df.tail(7).index)
enc_git_df['Date'] = pd.to_datetime(enc_git_df['Date'])
# enc_git_df = enc_git_df[enc_git_df['Date']<=enc_agg['Date'].min()]
enc_out_df = pd.concat([enc_git_df, enc_agg])
enc_out_df["Site"] = "Encina"
# enc_out_df = enc_out_df[['Date', 'BA.1', 'BA.1.1.X', 'BA.2.X', 'BA.2.12.X', 'BA.4.X', 'BA.5.X', 'BA.2.75', 'BA.4.6', 'BQ.1.X', 'BQ.1.1.X', 'BF.7.X', 'XBB.X', 'XBB.1.5.X', 'XBB.1.9.X', 'XBB.1.16.X', 'XBB.2.3.X', 'EG.5.X', 'BA.2.86.X', 'HV.1.X', 'JN.1.X', 'JN.1.7.X', 'JN.1.4.X', 'KQ.1.X', 'JN.1.11.X', 'KP.2.X', 'Recombinants', 'Other']]
enc_out_df = enc_out_df.fillna(0.00).round(2).drop_duplicates(subset=['Date'],keep='first')
enc_out_df = enc_out_df.sort_values(by=['Date'])
# enc_out_df.to_csv('Encina_sewage_seqs.csv', index=False)
# enc_out_df.to_csv('freyja_reports/output/Encina_sewage_seqs.csv')
sb_agg['Date'] = pd.to_datetime(sb_agg['Date'], format='%Y-%m-%d')
sb_git_df = pd.read_csv("https://raw.githubusercontent.com/andersen-lab/SARS-CoV-2_WasteWater_San-Diego/master/SouthBay_sewage_seqs.csv")
# sb_git_df = sb_git_df.drop(sb_git_df.tail(8).index)
sb_git_df['Date'] = pd.to_datetime(sb_git_df['Date'])
# sb_git_df = sb_git_df[sb_git_df['Date']<=sb_agg['Date'].min()]
sb_out_df = pd.concat([sb_git_df, sb_agg])
sb_out_df["Site"] = "South Bay"
# sb_out_df = sb_out_df[['Date', 'BA.1', 'BA.1.1.X', 'BA.2.X', 'BA.2.12.X', 'BA.4.X', 'BA.5.X', 'BA.2.75', 'BA.4.6', 'BQ.1.X', 'BQ.1.1.X', 'BF.7.X', 'XBB.X', 'XBB.1.5.X', 'XBB.1.9.X', 'XBB.1.16.X', 'XBB.2.3.X', 'EG.5.X', 'BA.2.86.X', 'HV.1.X', 'JN.1.X', 'JN.1.7.X', 'JN.1.4.X', 'KQ.1.X', 'JN.1.11.X', 'KP.2.X', 'Recombinants', 'Other']]
sb_out_df = sb_out_df.fillna(0.00).round(2).drop_duplicates(subset=['Date'],keep='first')
sb_out_df = sb_out_df.sort_values(by=['Date'])
# sb_out_df.to_csv('SouthBay_sewage_seqs.csv', index=False)
pd.concat([pl_out_df, enc_out_df, sb_out_df]).fillna(0.00).to_csv('SD_Sewage_Seqs_Complete.csv', index=False)
SD_formatted_agg = pd.concat([pl_out_df, enc_out_df, sb_out_df])
SD_formatted_agg = SD_formatted_agg.fillna(0.00).round(2).drop_duplicates(subset=['Date'],keep='first')


for key in plot_config_.keys():
	if key != "Other":
		SD_formatted_agg[plot_config_[key]["name"]] = SD_formatted_agg[list(set(SD_formatted_agg.columns).intersection(set(plot_config_[key]["members"])))].sum(axis=1)
		SD_formatted_agg[plot_config_[key]["name"]] = SD_formatted_agg[plot_config_[key]["name"]].where(SD_formatted_agg[plot_config_[key]["name"]] <= 100, 100)

selected_columns = [plot_config_[key]["name"] for key in plot_config_.keys() if plot_config_[key]["name"] in SD_formatted_agg.columns]
selected_columns[0:0] = ["Date", "Site"]
SD_formatted_agg = SD_formatted_agg[selected_columns]


data_columns = SD_formatted_agg.columns.difference(["Date", "Site"])

# SD_formatted_agg.loc[SD_formatted_agg[data_columns].sum(axis=1) >= 100, data_columns] = SD_formatted_agg.loc[SD_formatted_agg[data_columns].sum(axis=1) >= 100, data_columns].div(SD_formatted_agg[data_columns].sum(axis=1), axis=0)

SD_formatted_agg['Other'] = 100 - SD_formatted_agg[data_columns].sum(axis=1)
SD_formatted_agg['Other'] = SD_formatted_agg['Other'].round(1)
# Remove possible < 0 values due to roundup operations
SD_formatted_agg['Other'] = SD_formatted_agg['Other'].where(abs(SD_formatted_agg['Other']) > 0.4, 0)
SD_formatted_agg.fillna(0.00).to_csv('SD_Sewage_Seqs_Output.csv', index=False)


