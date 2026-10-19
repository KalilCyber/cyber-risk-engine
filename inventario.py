class Inventario:
    
    def __init__(self, ativos=None):

        if ativos is None:
            self.ativos = []
        else:
          self.ativos = ativos
    
    def cadastrar_ativo(self, ativo):

        for ativo_existente in self.ativos:

            if ativo_existente.id == ativo.id:
                raise ValueError(f"Já existe um ativo com o ID {ativo.id}.")
        
        self.ativos.append(ativo)
    
    def listar_ativos(self):
        
        return self.ativos.copy()
    
    def buscar_por_id(self, id_ativo):

        for ativo in self.ativos:

            if ativo.id == id_ativo:
                return ativo
        
        return None
    
    def buscar_por_nome(self, nome):

        resultados = []

        for ativo in self.ativos:

            if nome.lower() in ativo.nome.lower():
                resultados.append(ativo)
        
        return resultados

    def atualizar_ativo(self, id_ativo, nome=None, responsavel=None, setor=None,
                        atributo_especifico=None):

        ativo = self.buscar_por_id(id_ativo)

        if ativo is None:
            return False

        if nome is not None:
            ativo.nome = nome

        if responsavel is not None:
            ativo.responsavel = responsavel

        if setor is not None:
            ativo.setor = setor

        if atributo_especifico is not None:

            if hasattr(ativo, "processador"):
                ativo.processador = atributo_especifico

            elif hasattr(ativo, "servico"):
                ativo.servico = atributo_especifico

            elif hasattr(ativo, "endereco_ip"):
                ativo.endereco_ip = atributo_especifico

            elif hasattr(ativo, "url"):
                ativo.url = atributo_especifico

        

        return True

    def remover_ativo(self, id_ativo):

        ativo = self.buscar_por_id(id_ativo)

        if ativo is None:
            return False

        self.ativos.remove(ativo)

        return True

    
    def buscar_vulnerabilidade_por_id(
        self,
        id_vulnerabilidade):

        for ativo in self.ativos:

            for vulnerabilidade in ativo.vulnerabilidades:

                if vulnerabilidade.id == id_vulnerabilidade:

                    return vulnerabilidade

        return None

    def buscar_vulnerabilidade_por_cve(
        self,
        cve_id):

        if cve_id is None:
            return None

        for ativo in self.ativos:

            for vulnerabilidade in ativo.vulnerabilidades:

                if (
                    vulnerabilidade.cve_id
                    and vulnerabilidade.cve_id.upper() == cve_id.upper()):

                    return vulnerabilidade

        return None

    
    def associar_vulnerabilidade(
            self,
            id_ativo,
            vulnerabilidade
        ):

            ativo = self.buscar_por_id(
                id_ativo
            )


            if ativo is None:
                return False
            
            # VERIFICA DUPLICIDADE DENTRO DO MESMO ATIVO

            for vulnerabilidade_existente in ativo.vulnerabilidades:

                # Mesmo ID interno no mesmo ativo
                if (
                    vulnerabilidade_existente.id
                    == vulnerabilidade.id
                ):

                    raise ValueError(
                        f"Já existe uma vulnerabilidade com o ID "
                        f"{vulnerabilidade.id} associada ao ativo "
                        f"{ativo.nome}."
                    )


                # Mesmo CVE no mesmo ativo
                if (
                    vulnerabilidade.cve_id
                    and vulnerabilidade_existente.cve_id
                    and vulnerabilidade_existente.cve_id.upper()
                    == vulnerabilidade.cve_id.upper()
                ):

                    raise ValueError(
                        f"O CVE {vulnerabilidade.cve_id} "
                        "já está associado a este ativo."
                    )

 
            # CONSISTÊNCIA GLOBAL DO CVE

            if vulnerabilidade.cve_id:

                vulnerabilidade_global = (
                    self.buscar_vulnerabilidade_por_cve(
                        vulnerabilidade.cve_id
                    )
                )


                if vulnerabilidade_global is not None:

                    # O mesmo CVE precisa possuir
                    # a mesma severidade.
                    if (
                        vulnerabilidade_global.severidade
                        != vulnerabilidade.severidade
                    ):

                        raise ValueError(
                            f"O CVE {vulnerabilidade.cve_id} "
                            "já existe no inventário com uma "
                            "severidade diferente."
                        )

           
            # VULNERABILIDADE MANUAL
           
            else:

                vulnerabilidade_global = (
                    self.buscar_vulnerabilidade_por_id(
                        vulnerabilidade.id
                    )
                )


                if vulnerabilidade_global is not None:

                    if not (
                        vulnerabilidade_global
                        .possui_mesmos_dados(
                            vulnerabilidade
                        )
                    ):

                        raise ValueError(
                            f"O ID {vulnerabilidade.id} já pertence "
                            "a outra vulnerabilidade com "
                            "dados diferentes."
                        )


            # IMPORTANTE:
            # Não reutilizamos o objeto de outro ativo.
            ativo.adicionar_vulnerabilidade(
                vulnerabilidade
            )


            return True
    
    def buscar_vulnerabilidade_no_ativo(
            self,
            id_ativo,
            id_vulnerabilidade):
    
        ativo = self.buscar_por_id(id_ativo)

        if ativo is None:
            return None
        
        for vulnerabilidade in ativo.vulnerabilidades:
            if vulnerabilidade.id == id_vulnerabilidade:
                return vulnerabilidade
        
        return None
    
    def atualizar_vulnerabilidade(
            self,
            id_ativo,
            id_vulnerabilidade,
            descricao=None,
            categoria=None,
            severidade=None,
            status=None
    ):
        
        vulnerabilidade = (self.buscar_vulnerabilidade_no_ativo(
                           id_ativo,
                           id_vulnerabilidade))
        
        if vulnerabilidade is None:
            return False
        
        vulnerabilidade.atualizar(
            descricao,
            categoria,
            severidade,
            status
        )

        return True
        

    
    def listar_vulnerabilidades(self, id_ativo):

        ativo = self.buscar_por_id(id_ativo)

        if ativo is None:
            return None

        return ativo.vulnerabilidades.copy()

    def cadastrar_dependencia(
        self,
        id_ativo_destino,
        id_ativo_origem,
        nivel
    ):

        ativo_destino = self.buscar_por_id(
            id_ativo_destino
        )

        ativo_origem = self.buscar_por_id(
            id_ativo_origem
        )


        if ativo_destino is None:

            raise ValueError(
                "Ativo de destino não encontrado."
            )


        if ativo_origem is None:

            raise ValueError(
                "Ativo de origem não encontrado."
            )


        ativo_destino.adicionar_dependencia(
            id_ativo_origem,
            nivel
        )


        return True
