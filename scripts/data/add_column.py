def add_column(texto: str) ->str:
    # elimino las comas
    # MLA,123 -> MLA123 clave del producto
    # concateno el resultado al texto original
    # MLA,123 -> MLA,123,MLA123 
    return texto+","+texto.replace(",","")