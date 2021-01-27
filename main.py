import openpyxl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from datetime import datetime
from tqdm import tqdm
from scipy.stats import poisson, skellam
from scipy.optimize import minimize
import statsmodels.api as sm
import statsmodels.formula.api as smf
from poisson_func import * 

plt.style.use('ggplot')
plt.rcParams["figure.figsize"] = (16,9) 


new_sim = True
N_sim = 50000


df = pd.read_csv("matches_chile.csv")
df_tabla_2019 = pd.read_csv("Tabla2019.csv", index_col = "Equipo")
df_tabla_2019.sort_values(by=["PTS","DG"], ascending = False, inplace = True)
teams = df.Local.unique()
poisson_model = fit_poisson_model(df)


if new_sim == False:
    df_tabla_2020 = pd.read_csv("Tabla2020.csv", index_col = "Equipo")
    sim_poisson_local = pd.read_csv("sim_poisson_local.csv", index_col = [0,1])
    sim_poisson_local.columns = range(1, N_sim + 1)
    sim_poisson_visita = pd.read_csv("sim_poisson_visita.csv", index_col = [0,1])
    sim_poisson_visita.columns = range(1, N_sim + 1)
    df_posicion = pd.read_csv("df_posicion.csv", index_col = 0)
    df_desc_stats = pd.read_csv("df_desc_stats.csv", index_col = 0)
    summary_reasons = pd.read_excel("resumen_descenso.xlsx", index_col = 0)
    df_cd3 = pd.read_csv("df_cd3.csv", index_col = 0)
    df_rel_matches = pd.read_csv("df_rel_matches.csv", index_col = 0)
else:
    np.random.seed(42)
    #plot_poisson_dist(df)
    print("Construyendo tabla 2020")
    df_tabla_2020 = current_table(df, teams)
    df_posicion = pd.DataFrame(columns = ['Equipo', 'Tabla', 'n_sim', 'Posición'])
    print("Simulando partidos restantes del 2020")
    sim_poisson_local, sim_poisson_visita = poisson_tournament(df, poisson_model, N = N_sim)
    print("Summary positions")
    df_posicion = summary_positions(sim_poisson_local, sim_poisson_visita, N_sim, teams, df_tabla_2019,
                                        df_tabla_2020)
    print("Relegation stats")
    df_desc_stats = relegation_stats(N_sim, df_posicion, poisson_model)
    summary_reasons = create_summary_reasons(df_desc_stats, N_sim)
    df_cd3, df_rel_matches = cases_distribution(df_posicion, N_sim)

print("Prob de campeonar")
p = df_posicion[(df_posicion["Posición"] == 1)&(df_posicion.Tabla == "Absoluta")].Equipo.value_counts()/N_sim
print(p)

df_cc_uch = df_rel_matches[(df_rel_matches.team_1.isin(["Colo-Colo","Universidad de Chile"]))&
               (df_rel_matches.team_2.isin(["Colo-Colo","Universidad de Chile"]))]
prob_definicion_uch_cc = df_cc_uch.shape[0]/N_sim
print("Porcentaje de CC vs UCH:", 100*prob_definicion_uch_cc, "%")
df_cc_uch.head()


# df_ult_abs = df_posicion[(df_posicion.Tabla == "Absoluta")&
#             (df_posicion["Posición"] == 18)&
#             (df_posicion["Equipo"] == "Universidad de Chile")]
# print(df_ult_abs.shape[0]/N_sim)

# df_pen_abs = df_posicion[(df_posicion.Tabla == "Absoluta")&
#             (df_posicion["Posición"] == 17)&
#             (df_posicion["Equipo"] == "Universidad de Chile")]
# print(df_pen_abs.shape[0]/N_sim)

# df_ult_pon = df_posicion[(df_posicion.Tabla == "Ponderada")&
#             (df_posicion["Posición"] == 18)&
#             (df_posicion["Equipo"] == "Universidad de Chile")]
# sim_ult_pon = df_ult_pon.n_sim
# print(df_ult_pon.shape[0]/N_sim)

# df_pen_pon = df_posicion[(df_posicion.Tabla == "Ponderada")&
#             (df_posicion["Posición"] == 17)&
#             (df_posicion["Equipo"] == "Universidad de Chile")]
# sim_pen_pon = df_pen_pon.n_sim
# print(df_pen_pon.shape[0]/N_sim)


print("Probabilidades de descenso")
print(summary_reasons)

print("Exportando probabilidades por equipo")
for team in teams:
    print(team)
    probs_relegation(team, df_posicion, N_sim)