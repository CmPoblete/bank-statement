# Supuestos

- Los movimientos entregados por los bancos no stan ordenados de ninguna manera especial (puede variar para el mismo banco).

- Los movimientos con numero de documento 0000000000 y que no sea transferencia pertenecen a cheques.

- Los datos de las consultas son correctos (esto es dado que el fetched_at del archivo "empresa_C_13_01_2021.json" es el mismo que el del archivo "empresa_C_12_01_2021.json" mientras que deberian tener un dia de diferencia).

- Al utilizar la funcion update no se utilizara un snapshot mas antiguo que el ultimo usado.


# Estructura de la solucion

```
BankStatement {
    dates {
        movements: {
            Movement,
            last_update: str
        },
        completed: bool
    },

    movements_order = [str]
}
```
Esta clase tiene un hash en el que cada key es una fecha en formato YYYY-MM-DD, En estos se guarda otro hash con los movements segun la post_date de cada uno y un booleano que dice si el dia ya esta completo o no.

Luego dentro de los movements se tiene el objeto movement que aprece en la docuemntacion de Fintoc y un string representando la fecha del ultimo snapshot en el que se reviso el movement.

La logica es la siguiente, para hacer mas eficiente en termino de velocidad para cada update de los datos, se utilizan hashes, asi no se pierde tiempo teniendo que buscar cada movement. Primero, se revisa el post_date del movement entregado por el banco. Si no eixiste esta fecha como key se crea. Luego, se revisa si esta fecha esta completa (si esta fecha habia sido revisada en un snapshot posterior a esta). Si estaba completa se salta hasta el siguiente movement, en caso contrario, se revisa si el movement fue creado. Para esto, se revisa si tiene id para usarlo como key del hash de movements. En caso de no tener, se crea una key concatenando el monto, con "i"/"o" (i para inbound y o para outbound) y un contador en caso de que haya mas de un movimiento con ese monto y tipo para la fecha dada (el formato seria algo asi: "5000-i-0"). Despues de esto, se revisa si existe un movimiento con esta key y si la fecha de actualizacion corresponde a otra que no sea este snapshot. Si ya fue revisada por este snapshot se repite el proceso para la misma key, pero con un contador mayor (ej: "5000-i-1"). Si se encuentra un movement con esa key que no hay sido revisada en este snapshot, se actualiza la fecha y termina la revision de este movemet porque significa que ya habia sido creado. Si no existe value para esta key, se crea el movment parseando los datos para que corresponda con el objeto Movement de la documentacion.

Adicionalmente, para que show_movements sea veloz, tome la decision de tener un segundo hash en el que se se agrupa por fechas y en cada fecha se almacena la key de sus movements pero ordenadas segun post_dates de sus values. Cuando se crea un nuevo movement, se revisa el arreglo correspondiente a la fecha de este en movements_order y se inserta en la posicion correspondiente. Con esto se logra que la complejidad de show_movements sea de O(n) aumentando un poco la complejidad de actualizar los datos.   