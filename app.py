from flask import Flask, render_template, request, jsonify
import traceback
from src.data_loader import load_data, get_countries, get_continents
from src.data_cleaner import clean_data, get_latest_data
from src.analysis import (
    get_top_countries_by_cases,
    get_top_countries_by_deaths,
    get_death_rate_comparison,
    get_continent_comparison,
    get_country_timeline,
    get_monthly_trends,
    get_comparison_data,
    get_name_col,
    get_world_map_data
)
from src.visualizations import (
    plot_top_countries_cases,
    plot_top_countries_deaths,
    plot_death_rate_comparison,
    plot_continent_comparison,
    plot_country_timeline,
    plot_monthly_trends,
    plot_multi_country_comparison,
    plot_world_map,
    plot_daily_trends_with_average
)

app = Flask(__name__)

print("Loading and cleaning data...")
raw_df = load_data()
df = clean_data(raw_df)
countries = get_countries(df)
continents = get_continents(df)
name_col = get_name_col(df)
print(f"Data loaded! Using '{name_col}' as country identifier.")
print(f"Found {len(countries)} countries and {len(continents)} continents.")

@app.route('/')
def index():
    return render_template('index.html', countries=countries, continents=continents)

@app.route('/api/overview')
def overview():
    try:
        latest = get_latest_data(df)
        total_cases = int(latest['total_cases'].sum())
        total_deaths = int(latest['total_deaths'].sum())
        countries_affected = len(latest)
        global_death_rate = round(total_deaths / total_cases * 100, 2) if total_cases > 0 else 0
        
        return jsonify({
            'total_cases': total_cases,
            'total_deaths': total_deaths,
            'countries_affected': countries_affected,
            'global_death_rate': global_death_rate
        })
    except Exception as e:
        print(f"Error in overview: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-cases')
def top_cases():
    try:
        top = get_top_countries_by_cases(df, 10)
        chart = plot_top_countries_cases(top)
        return jsonify({'chart': chart})
    except Exception as e:
        print(f"Error in top-cases: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-deaths')
def top_deaths():
    try:
        top = get_top_countries_by_deaths(df, 10)
        chart = plot_top_countries_deaths(top)
        return jsonify({'chart': chart})
    except Exception as e:
        print(f"Error in top-deaths: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/death-rates')
def death_rates():
    try:
        rates = get_death_rate_comparison(df, 15)
        chart = plot_death_rate_comparison(rates)
        return jsonify({'chart': chart})
    except Exception as e:
        print(f"Error in death-rates: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/continents')
def continent_stats():
    try:
        stats = get_continent_comparison(df)
        chart = plot_continent_comparison(stats)
        data = stats.to_dict(orient='records') if not stats.empty else []
        return jsonify({'chart': chart, 'data': data})
    except Exception as e:
        print(f"Error in continents: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/country/<country>')
def country_data(country):
    try:
        timeline = get_country_timeline(df, country)
        
        if len(timeline) == 0:
            return jsonify({
                'chart': None,
                'summary': {
                    'total_cases': 0,
                    'total_deaths': 0,
                    'latest_date': 'N/A'
                },
                'error': 'No data found for this country'
            })
        
        chart = plot_country_timeline(timeline, country)
        
        latest = timeline.iloc[-1]
        summary = {
            'total_cases': int(latest['total_cases']) if latest is not None else 0,
            'total_deaths': int(latest['total_deaths']) if latest is not None else 0,
            'latest_date': str(latest['date'].date()) if latest is not None else 'N/A'
        }
        
        return jsonify({'chart': chart, 'summary': summary})
    except Exception as e:
        print(f"Error in country data: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/country-monthly/<country>')
def country_monthly(country):
    try:
        monthly = get_monthly_trends(df, country)
        chart = plot_monthly_trends(monthly, country)
        return jsonify({'chart': chart})
    except Exception as e:
        print(f"Error in country-monthly: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/country-daily/<country>')
def country_daily(country):
    try:
        timeline = get_country_timeline(df, country)
        chart = plot_daily_trends_with_average(timeline, country)
        return jsonify({'chart': chart})
    except Exception as e:
        print(f"Error in country-daily: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare')
def compare_countries():
    try:
        selected = request.args.getlist('countries')
        if not selected:
            return jsonify({'error': 'No countries selected'}), 400
        
        comparison_df, col_name = get_comparison_data(df, selected)
        chart = plot_multi_country_comparison(comparison_df, selected, col_name)
        return jsonify({'chart': chart, 'countries': selected})
    except Exception as e:
        print(f"Error in compare: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/world-map')
def world_map():
    try:
        map_data = get_world_map_data(df)
        chart = plot_world_map(map_data)
        return jsonify({'chart': chart})
    except Exception as e:
        print(f"Error in world-map: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)