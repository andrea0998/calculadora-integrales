from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from sympy import symbols, integrate, sympify, lambdify
import matplotlib.pyplot as plt
import numpy as np
import io

x, y, z = symbols('x y z')  # ← define las 3 variables desde el inicio

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')


def generar_pasos_integral_doble(expr_str, xlim, ylim):
    from sympy import symbols, sympify, integrate, lambdify

    x, y = symbols('x y')
    expr = sympify(expr_str)

    a, b = map(float, xlim)
    c, d = map(float, ylim)

    Fx = integrate(expr, x)
    pasos = [f"Paso 1: Integrar respecto a x: ∫ {expr} dx = {Fx}"]

    Fx_lambda = lambdify(x, Fx, 'numpy')
    Fxb = Fx_lambda(b)
    Fxa = Fx_lambda(a)
    Fx_def = Fxb - Fxa
    pasos.append(f"Evaluar en x = [{a}, {b}]: F({b}) - F({a}) = {Fxb} - {Fxa} = {Fx_def}")

    Fy = integrate(Fx_def, y)
    pasos.append(f"Paso 2: Integrar respecto a y: ∫ {Fx_def} dy = {Fy}")

    Fy_lambda = lambdify(y, Fy, 'numpy')
    Fyd = Fy_lambda(d)
    Fyc = Fy_lambda(c)
    Fy_def = Fyd - Fyc
    pasos.append(f"Evaluar en y = [{c}, {d}]: F({d}) - F({c}) = {Fyd} - {Fyc} = {Fy_def}")

    pasos.append(f"Resultado final: {Fy_def}")
    return pasos, Fy_def

def generar_pasos_integral_triple(expr_str, xlim, ylim, zlim):
    from sympy import symbols, sympify, integrate, lambdify

    x, y, z = symbols('x y z')
    expr = sympify(expr_str)

    a, b = map(float, xlim)
    c, d = map(float, ylim)
    e, f = map(float, zlim)

    pasos = []

    # Paso 1: integrar respecto a x
    Fx = integrate(expr, x)
    pasos.append(f"Paso 1: Integrar respecto a x: ∫ {expr} dx = {Fx}")
    Fx_lambda = lambdify(x, Fx, 'numpy')
    Fxb = Fx_lambda(b)
    Fxa = Fx_lambda(a)
    Fx_def = Fxb - Fxa
    pasos.append(f"Evaluar en x = [{a}, {b}]: F({b}) - F({a}) = {Fxb} - {Fxa} = {Fx_def}")

    # Paso 2: integrar respecto a y
    Fy = integrate(Fx_def, y)
    pasos.append(f"Paso 2: Integrar respecto a y: ∫ {Fx_def} dy = {Fy}")
    Fy_lambda = lambdify(y, Fy, 'numpy')
    Fyd = Fy_lambda(d)
    Fyc = Fy_lambda(c)
    Fy_def = Fyd - Fyc
    pasos.append(f"Evaluar en y = [{c}, {d}]: F({d}) - F({c}) = {Fyd} - {Fyc} = {Fy_def}")

    # Paso 3: integrar respecto a z
    Fz = integrate(Fy_def, z)
    pasos.append(f"Paso 3: Integrar respecto a z: ∫ {Fy_def} dz = {Fz}")
    Fz_lambda = lambdify(z, Fz, 'numpy')
    Fzf = Fz_lambda(f)
    Fze = Fz_lambda(e)
    Fz_def = Fzf - Fze
    pasos.append(f"Evaluar en z = [{e}, {f}]: F({f}) - F({e}) = {Fzf} - {Fze} = {Fz_def}")

    pasos.append(f"Resultado final: {Fz_def}")
    return pasos, Fz_def

@app.route('/integrate', methods=['POST'])
def calculate():
    data = request.json
    tipo = data.get('tipo', 'simple')
    expr = sympify(data['function'])
    steps = []
    result = None

    try:
        if tipo == 'simple':
            result_expr = integrate(expr, x)
            if data.get('limits'):
                try:
                    a, b = map(sympify, data['limits'].split(','))
                    steps.append(f"Paso 1: F(x) = ∫ {expr} dx = {result_expr}")
                    F = lambdify(x, result_expr, 'numpy')
                    Fa = F(float(a))
                    Fb = F(float(b))
                    steps.append(f"Paso 2: Evaluar F({b}) - F({a}) = {Fb} - {Fa}")
                    final_result = Fb - Fa
                    steps.append(f"Resultado final: {final_result}")
                    return jsonify({
                        'result': str(final_result),
                        'steps': '<br/><br/>'.join(steps)
                    })
                except:
                    steps.append(f"Resultado: ∫ {expr} dx = {result_expr} + C")
                    return jsonify({
                        'result': str(result_expr) + ' + C',
                        'steps': '<br/><br/>'.join(steps)
                    })
            else:
                steps.append(f"Resultado: ∫ {expr} dx = {result_expr} + C")
                return jsonify({
                    'result': str(result_expr) + ' + C',
                    'steps': '<br/><br/>'.join(steps)
                })

        elif tipo == 'doble':
            limits = data['limits'].split(';')
            if len(limits) != 2:
                return jsonify({'error': 'Debes proporcionar 2 pares de límites (ej: a,b;c,d)'}), 400
            try:
                a, b = map(sympify, limits[0].split(','))
                c, d = map(sympify, limits[1].split(','))
                pasos, resultado = generar_pasos_integral_doble(data['function'], (a, b), (c, d))
                return jsonify({
                    'result': str(resultado),
                    'steps': '<br/><br/>'.join(pasos)
                })
            except Exception as e:
                return jsonify({'error': f'Límites inválidos o error en cálculo: {e}'}), 400

        elif tipo == 'triple':
            limits = data['limits'].split(';')
            if len(limits) != 3:
                return jsonify({'error': 'Debes proporcionar 3 pares de límites (ej: a,b;c,d;e,f)'}), 400
            try:
                a, b = map(sympify, limits[0].split(','))
                c, d = map(sympify, limits[1].split(','))
                e, f = map(sympify, limits[2].split(','))
                pasos, resultado = generar_pasos_integral_triple(data['function'], (a, b), (c, d), (e, f))
                return jsonify({
                    'result': str(resultado),
                    'steps': '<br/><br/>'.join(pasos)
                })
            except Exception as e:
                return jsonify({'error': f'Límites inválidos o error en cálculo: {e}'}), 400

        else:
            return jsonify({'error': 'Tipo de integral no soportado'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/graph', methods=['POST'])
def graph():
    data = request.json
    try:
        expr = sympify(data['function'])
        integral_result = integrate(expr, x)
        f = lambdify(x, integral_result, 'numpy')

        # Límites personalizados o por defecto
        if 'limits' in data and data['limits']:
            a, b = map(float, data['limits'].split(','))
        else:
            a, b = -10, 10

        X = np.linspace(a, b, 500)
        Y = f(X)

        # Convertir a listas normales para enviarlos como JSON
        return jsonify({
            'x': X.tolist(),
            'y': Y.tolist(),
            'expression': str(integral_result)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/graph2d', methods=['POST'])
def graph2d():
    data = request.json
    try:
        expr = sympify(data['function'])

        # Extraer límites
        if 'limits' in data and data['limits']:
            try:
                lims = data['limits'].split(';')
                a, b = map(float, lims[0].split(','))
                c, d = map(float, lims[1].split(','))
            except:
                return jsonify({'error': 'Límites inválidos para integral doble'}), 400
        else:
            a, b, c, d = -5, 5, -5, 5

        x_vals = np.linspace(a, b, 40)
        y_vals = np.linspace(c, d, 40)
        X, Y = np.meshgrid(x_vals, y_vals)

        f = lambdify((x, y), expr, 'numpy')
        Z = f(X, Y)

        return jsonify({
            'x': x_vals.tolist(),
            'y': y_vals.tolist(),
            'z': Z.tolist(),
            'expression': str(expr)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400
        
@app.route('/graph3d', methods=['POST'])
def graph3d():
    data = request.json
    try:
        expr = sympify(data['function'])
        limits = data['limits'].split(';')
        if len(limits) != 3:
            return jsonify({'error': 'Debes proporcionar 3 pares de límites (ej: a,b;c,d;e,f)'}), 400

        a, b = map(float, limits[0].split(','))
        c, d = map(float, limits[1].split(','))
        e, f = map(float, limits[2].split(','))

        # Crea una animación de cortes a distintos valores de z
        z_slices = np.linspace(e, f, 10)
        x_vals = np.linspace(a, b, 40)
        y_vals = np.linspace(c, d, 40)
        X, Y = np.meshgrid(x_vals, y_vals)

        f_xyz = lambdify((x, y, z), expr, 'numpy')
        frames = []

        for z_val in z_slices:
            try:
                Z = f_xyz(X, Y, z_val)
                if not np.shape(Z) == X.shape:
                    raise ValueError("Shape mismatch al evaluar Z")
                if np.any(np.isnan(Z)) or np.any(np.isinf(Z)):
                    raise ValueError("Valores inválidos en Z")
                frames.append({
                    'z_value': float(z_val),
                    'z_data': Z.tolist()
                })
            except Exception as err:
                # Salta este corte si no se puede calcular
                continue

        if not frames:
            return jsonify({'error': 'No se pudieron generar cortes válidos para z'}), 400

        return jsonify({
            'x': x_vals.tolist(),
            'y': y_vals.tolist(),
            'frames': frames
        })

    except Exception as e:
        return jsonify({'error': f'Error en el servidor: {e}'}), 400



if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
