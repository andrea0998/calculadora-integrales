from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from sympy import symbols, integrate, sympify, lambdify
import matplotlib.pyplot as plt
import numpy as np
import io

x = symbols('x')

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

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
                    # Si los límites no son válidos, mostrar solo la primitiva
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
            y = symbols('y')
            limits = data['limits'].split(';')
            a, b = map(sympify, limits[0].split(','))
            c, d = map(sympify, limits[1].split(','))
            result = integrate(expr, (x, a, b), (y, c, d))
            steps.append(f"Resultado: ∬ {expr} dx dy = {result}")
            return jsonify({'result': str(result), 'steps': '<br/><br/>'.join(steps)})

        elif tipo == 'triple':
            y, z = symbols('y z')
            limits = data['limits'].split(';')
            a, b = map(sympify, limits[0].split(','))
            c, d = map(sympify, limits[1].split(','))
            e, f = map(sympify, limits[2].split(','))
            result = integrate(expr, (x, a, b), (y, c, d), (z, e, f))
            steps.append(f"Resultado: ∭ {expr} dx dy dz = {result}")
            return jsonify({'result': str(result), 'steps': '<br/><br/>'.join(steps)})

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

        # Determinar límites de integración
        if 'limits' in data and data['limits']:
            a, b = map(float, data['limits'].split(','))
            show_limits = True
        else:
            a, b = -10, 10
            show_limits = False

        X = np.linspace(a, b, 500)
        Y = f(X)

        fig, ax = plt.subplots()
        ax.plot(X, Y, label=f"F(x) = {integral_result}", color='green')


        # Si es definida, marcar los límites
        if show_limits:
            ax.axvline(x=a, color='blue', linestyle='--', label=f"x = {a}")
            ax.axvline(x=b, color='red', linestyle='--', label=f"x = {b}")
            ax.fill_between(X, Y, alpha=0.2, color='green')

        ax.set_title(f'Gráfica de la integral ∫({expr}) dx')
        ax.set_xlabel('x')
        ax.set_ylabel('F(x)')
        ax.grid(True)
        ax.legend()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
