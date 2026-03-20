from freyja.utils import prepLineageDict
import pandas as pd
# below supresses SettingWithCopyWarning
pd.options.mode.chained_assignment = None
from datetime import date,timedelta,datetime
import yaml

def get_col_date(short_name, site):
    col_date = short_name.removeprefix(site)
    day = ''
    if 'JAN' in col_date:
        month = 1
        day = col_date.strip('JAN')
    elif 'FEB' in col_date:
        month = 2
        day = col_date.strip('FEB')
    elif 'MAR' in col_date:
        month = 3
        day = col_date.strip('MAR')
    elif 'APR' in col_date:
        month = 4
        day = col_date.strip('APR')
    elif 'MAY' in col_date:
        month = 5
        day = col_date.strip('MAY')
    elif 'JUN' in col_date:
        month = 6
        day = col_date.strip('JUN')
    elif 'JUL' in col_date:
        month = 7
        day = col_date.strip('JUL')
    elif 'AUG' in col_date:
        month = 8
        day = col_date.strip('AUG')
    elif 'SEP' in col_date:
        month = 9
        day = col_date.strip('SEP')
    elif 'OCT' in col_date:
        month = 10
        day = col_date.strip('OCT')
    elif 'NOV' in col_date:
        month = 11
        day = col_date.strip('NOV')
    elif 'DEC' in col_date:
        month = 12
        day = col_date.strip('DEC')
    return str(month) + '/' + str(day) + '/' + str(datetime.now().year)[-2:]
with open("plot_config.yml", "r" ) as f :
    plot_config = yaml.safe_load(f)
#make copy of config for later
plot_config_ = dict(plot_config)
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
agg_df = agg_df[agg_df['coverage'] > 75]
agg_df = prepLineageDict(agg_df,thresh=0.0000000001,config=plot_config,lineage_info=lineage_info)
formatted_agg = agg_df['linDict'].apply(pd.Series)
# drop any columns that aren't in the plot_config file
formatted_agg = formatted_agg[[key for key in plot_config_.keys() if key in formatted_agg.columns]]
#add abundance associated with things not in the plot config to recombinants or other
recombs = [fc for fc in formatted_agg.columns if (fc not in plot_config.keys()) and (fc[0]=='X')]
formatted_agg['Recombinants'] = formatted_agg[recombs].sum(axis=1)
#formatted_agg = formatted_agg.drop(columns=recombs)
others = [fc for fc in formatted_agg.columns if (fc not in plot_config.keys()) and fc!='Recombinants']
formatted_agg['Other'] = formatted_agg[others].sum(axis=1)
#formatted_agg = formatted_agg.drop(columns=others)
formatted_agg = formatted_agg.mul(100)
#separate out by site
formatted_agg['sample_name'] = formatted_agg.index
formatted_agg['sample_name'] = formatted_agg['sample_name'].apply(lambda x:x.split('__')[0])
pl_agg = formatted_agg[formatted_agg.index.str.contains('PL')]
enc_agg = formatted_agg[formatted_agg.index.str.contains('ENC')]
sb_agg = formatted_agg[formatted_agg.index.str.contains('SB')]
pl_agg = pl_agg.reset_index()
enc_agg = enc_agg.reset_index()
sb_agg = sb_agg.reset_index()
for i in range(len(pl_agg)):
    pl_agg['index'][i] = pl_agg['index'][i].replace(pl_agg['index'][i], get_col_date(pl_agg['index'][i].split('__')[0].split('_')[3], "PL"))
for i in range(len(enc_agg)):
    enc_agg['index'][i] = enc_agg['index'][i].replace(enc_agg['index'][i], get_col_date(enc_agg['index'][i].split('__')[0].split('_')[3], "ENC"))
for i in range(len(sb_agg)):
    sb_agg['index'][i] = sb_agg['index'][i].replace(sb_agg['index'][i], get_col_date(sb_agg['index'][i].split('__')[0].split('_')[3], "SB"))
pl_agg = pl_agg.rename(columns={"index": "collection_date"})
enc_agg = enc_agg.rename(columns={"index": "collection_date"})
sb_agg = sb_agg.rename(columns={"index": "collection_date"})


pl_agg = pl_agg[['sample_name','collection_date']]
pl_agg['geo_loc_name'] = 'Point Loma'
pl_agg['collection_date'] = pd.to_datetime(pl_agg['collection_date']).dt.strftime('%Y-%m-%d')
enc_agg = enc_agg[['sample_name','collection_date']]
enc_agg['geo_loc_name'] = 'Encina'
enc_agg['collection_date'] = pd.to_datetime(enc_agg['collection_date']).dt.strftime('%Y-%m-%d')
sb_agg = sb_agg[['sample_name','collection_date']]
sb_agg['geo_loc_name'] = 'South Bay'
sb_agg['collection_date'] = pd.to_datetime(sb_agg['collection_date']).dt.strftime('%Y-%m-%d')

meta_agg = pd.concat((pl_agg,enc_agg,sb_agg),axis=0).sort_values(by='collection_date')

meta_agg.to_csv('all-ww-metadata.csv',index=False)