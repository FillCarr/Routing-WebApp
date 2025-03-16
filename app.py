import os
from flask import Flask, jsonify, request, render_template
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'mydb'),
        user=os.environ.get('DB_USER', 'admin'),
        password=os.environ.get('DB_PASSWORD', 'password')
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/closest_vertex')
def closest_vertex():
    """
    Returns the nearest vertex (with EPSG:4326 coordinates) from edges_vertices_pgr 
    to the input point (lat and lng provided, assumed to be in EPSG:4326).
    Example: /closest_vertex?lat=41.55368&lng=-72.64610
    """
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    if lat is None or lng is None:
        return jsonify({"error": "lat and lng parameters are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    query = """
    SELECT id,
           ST_X(ST_Transform(the_geom,4326)) AS lng,
           ST_Y(ST_Transform(the_geom,4326)) AS lat,
           ST_Distance(
             ST_Transform(the_geom,4326),
             ST_Transform(ST_SetSRID(ST_Point(%s, %s),4326),4326)
           ) AS distance
    FROM edges_vertices_pgr
    ORDER BY distance
    LIMIT 1;
    """
    cur.execute(query, (lng, lat))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        # Debug print to server console.
        print(f"Input: lat={lat}, lng={lng} -> Closest vertex: {row[0]}, distance: {row[3]}")
        return jsonify({"id": row[0], "lng": row[1], "lat": row[2]})
    else:
        return jsonify({"error": "No vertex found"}), 404

@app.route('/shortest_route')
def shortest_route():
    """
    Computes and returns the shortest route between two vertices (by their IDs)
    as an ordered array of points (EPSG:4326).
    Example: /shortest_route?start=1&end=10
    """
    start = request.args.get('start', type=int)
    end = request.args.get('end', type=int)
    if start is None or end is None:
        return jsonify({"error": "start and end parameters are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    query = """
    SELECT r.seq, n.id,
           ST_X(ST_Transform(n.the_geom,4326)) AS lng,
           ST_Y(ST_Transform(n.the_geom,4326)) AS lat
    FROM get_shortest_route(%s, %s) r
    JOIN edges_vertices_pgr n ON n.id = r.node
    ORDER BY r.seq;
    """
    cur.execute(query, (start, end))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    if not rows:
        return jsonify({"error": "No route found"}), 404

    route_points = [{"seq": row[0], "id": row[1], "lng": row[2], "lat": row[3]} for row in rows]
    return jsonify(route_points)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
