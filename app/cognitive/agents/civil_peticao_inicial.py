"""
Agente: Petição Inicial Cível - Art. 319 CPC

⚠️ LEI 6: Este agente tem função única.
Gera assertions para petições iniciais cíveis.

Base Legal:
- CPC, art. 319: Requisitos da petição inicial
- CPC, art. 320: Documentos indispensáveis
"""
from typing import List, Dict
import json

from app.cognitive.agents.base import (
    BaseAgent,
    GeneratedAssertion,
    NormalizedInput,
    register_agent
)
from app.models.assertion import LegalSource
from app.core.config import settings


@register_agent
class PeticaoInicialCivilAgent(BaseAgent):
    """
    Agente especializado em Petições Iniciais Cíveis.
    
    ⚠️ LEI 5: Produz assertions, NÃO texto final.
    """
    
    agent_id = "peticao-inicial-civil"
    name = "Agente Petição Inicial Cível – Art. 319 CPC"
    legal_basis = "CPC, art. 319"
    legal_area = "civil"
    piece_type = "Petição Inicial"
    
    async def generate(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """
        Gera assertions para petição inicial.
        
        Estrutura da petição (Art. 319 CPC):
        I - o juízo a que é dirigida
        II - os nomes, os prenomes, o estado civil, a existência de união estável, 
             a profissão, o número de inscrição no CPF/CNPJ, o endereço eletrônico, 
             o domicílio e a residência do autor e do réu
        III - o fato e os fundamentos jurídicos do pedido
        IV - o pedido com as suas especificações
        V - o valor da causa
        VI - as provas com que o autor pretende demonstrar a verdade dos fatos alegados
        VII - a opção do autor pela realização ou não de audiência de conciliação/mediação
        """
        assertions = []
        position = 0
        
        # ===== SEÇÃO: QUALIFICAÇÃO DAS PARTES =====
        if input_data.partes:
            position += 1
            assertions.append(self._generate_qualificacao(
                input_data.partes,
                position,
                sources
            ))
        
        # ===== SEÇÃO: DOS FATOS =====
        for i, fato in enumerate(input_data.fatos):
            position += 1
            assertions.append(self._generate_fato(
                fato,
                position,
                i + 1,
                sources
            ))
        
        # ===== SEÇÃO: DO DIREITO / FUNDAMENTOS =====
        fundamentos = self._generate_fundamentos(
            input_data,
            sources,
            position
        )
        for fund in fundamentos:
            position += 1
            fund.position = position
            assertions.append(fund)
        
        # ===== SEÇÃO: DOS PEDIDOS =====
        for i, pedido in enumerate(input_data.pedidos):
            position += 1
            assertions.append(self._generate_pedido(
                pedido,
                position,
                i + 1,
                sources
            ))
        
        # ===== SEÇÃO: DO VALOR DA CAUSA =====
        if input_data.valor_causa:
            position += 1
            assertions.append(self._generate_valor_causa(
                input_data.valor_causa,
                position,
                sources
            ))
        
        # ===== SEÇÃO: DAS PROVAS =====
        position += 1
        assertions.append(self._generate_provas(position, sources))
        
        # ===== SEÇÃO: AUDIÊNCIA DE CONCILIAÇÃO =====
        position += 1
        assertions.append(self._generate_audiencia(position, sources))
        
        return assertions
    
    def _generate_qualificacao(
        self,
        partes: Dict[str, str],
        position: int,
        sources: Dict[str, LegalSource]
    ) -> GeneratedAssertion:
        """Gera assertion de qualificação das partes."""
        autor = partes.get("autor", "[AUTOR]")
        reu = partes.get("reu", "[RÉU]")
        
        text = f"{autor}, já qualificado nos autos, vem, respeitosamente, perante Vossa Excelência, propor a presente AÇÃO em face de {reu}, igualmente qualificado, pelos fatos e fundamentos a seguir expostos."
        
        return GeneratedAssertion(
            text=text,
            assertion_type="fato",
            confidence_level="alto",
            suggested_sources=["CPC, art. 319, II"],
            position=position
        )
    
    def _generate_fato(
        self,
        fato: str,
        position: int,
        numero: int,
        sources: Dict[str, LegalSource]
    ) -> GeneratedAssertion:
        """Gera assertion de fato."""
        return GeneratedAssertion(
            text=fato,
            assertion_type="fato",
            confidence_level="alto",  # Fatos vêm do usuário
            suggested_sources=[],  # Fatos não precisam de fonte legal
            position=position
        )
    
    def _generate_fundamentos(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource],
        start_position: int
    ) -> List[GeneratedAssertion]:
        """Gera assertions de fundamentos jurídicos."""
        fundamentos = []
        
        # Fundamento base: Art. 319 CPC
        if "CPC, art. 319" in sources:
            fundamentos.append(GeneratedAssertion(
                text="Nos termos do art. 319 do Código de Processo Civil, a petição inicial indicará o juízo a que é dirigida, os nomes das partes, o fato e os fundamentos jurídicos do pedido, bem como o pedido com suas especificações.",
                assertion_type="fundamento",
                confidence_level="alto",
                suggested_sources=["CPC, art. 319"],
                position=0  # Será atualizado
            ))
        
        # Fundamentos específicos baseados nos fatos
        fatos_lower = " ".join(input_data.fatos).lower()
        
        # Dano moral
        if "CC, art. 186" in sources:
            fundamentos.append(GeneratedAssertion(
                text="Aquele que, por ação ou omissão voluntária, negligência ou imprudência, violar direito e causar dano a outrem, ainda que exclusivamente moral, comete ato ilícito, nos termos do art. 186 do Código Civil.",
                assertion_type="fundamento",
                confidence_level="alto",
                suggested_sources=["CC, art. 186"],
                position=0
            ))
        
        # Responsabilidade civil
        if "CC, art. 927" in sources:
            fundamentos.append(GeneratedAssertion(
                text="Aquele que causar dano a outrem fica obrigado a repará-lo, conforme dispõe o art. 927 do Código Civil.",
                assertion_type="fundamento",
                confidence_level="alto",
                suggested_sources=["CC, art. 927"],
                position=0
            ))
        
        # CDC - Negativação indevida
        if "CDC, art. 43" in sources:
            fundamentos.append(GeneratedAssertion(
                text="O Código de Defesa do Consumidor, em seu art. 43, §2º, estabelece que a abertura de cadastro, ficha, registro e dados pessoais e de consumo deverá ser comunicada por escrito ao consumidor, quando não solicitada por ele.",
                assertion_type="fundamento",
                confidence_level="alto",
                suggested_sources=["CDC, art. 43"],
                position=0
            ))
        
        # Dano moral presumido (in re ipsa)
        if "Súmula 385 STJ" in sources or "negativação" in fatos_lower:
            fundamentos.append(GeneratedAssertion(
                text="A jurisprudência do Superior Tribunal de Justiça é pacífica no sentido de que o dano moral decorrente de inscrição indevida em cadastro de inadimplentes é presumido, dispensando prova do prejuízo efetivo (dano in re ipsa).",
                assertion_type="tese",
                confidence_level="medio",
                suggested_sources=["Súmula 385 STJ"] if "Súmula 385 STJ" in sources else [],
                position=0
            ))
        
        # CDC - Responsabilidade objetiva
        if "CDC, art. 14" in sources:
            fundamentos.append(GeneratedAssertion(
                text="O fornecedor de serviços responde, independentemente da existência de culpa, pela reparação dos danos causados aos consumidores por defeitos relativos à prestação dos serviços, conforme art. 14 do Código de Defesa do Consumidor.",
                assertion_type="fundamento",
                confidence_level="alto",
                suggested_sources=["CDC, art. 14"],
                position=0
            ))
        
        return fundamentos
    
    def _generate_pedido(
        self,
        pedido: str,
        position: int,
        numero: int,
        sources: Dict[str, LegalSource]
    ) -> GeneratedAssertion:
        """Gera assertion de pedido."""
        return GeneratedAssertion(
            text=f"Seja julgado procedente o pedido para {pedido}",
            assertion_type="pedido",
            confidence_level="alto",
            suggested_sources=["CPC, art. 319, IV"],
            position=position
        )
    
    def _generate_valor_causa(
        self,
        valor: float,
        position: int,
        sources: Dict[str, LegalSource]
    ) -> GeneratedAssertion:
        """Gera assertion de valor da causa."""
        return GeneratedAssertion(
            text=f"Atribui-se à causa o valor de R$ {valor:,.2f} (reais), para fins de alçada e recolhimento das custas processuais.",
            assertion_type="fato",
            confidence_level="alto",
            suggested_sources=["CPC, art. 319, V"],
            position=position
        )
    
    def _generate_provas(
        self,
        position: int,
        sources: Dict[str, LegalSource]
    ) -> GeneratedAssertion:
        """Gera assertion de provas."""
        return GeneratedAssertion(
            text="Requer a produção de todas as provas admitidas em direito, especialmente a documental, testemunhal e pericial, se necessário.",
            assertion_type="pedido",
            confidence_level="alto",
            suggested_sources=["CPC, art. 319, VI"],
            position=position
        )
    
    def _generate_audiencia(
        self,
        position: int,
        sources: Dict[str, LegalSource]
    ) -> GeneratedAssertion:
        """Gera assertion sobre audiência de conciliação."""
        return GeneratedAssertion(
            text="Manifesta-se o autor pelo interesse na realização de audiência de conciliação ou mediação, nos termos do art. 319, VII, do CPC.",
            assertion_type="pedido",
            confidence_level="alto",
            suggested_sources=["CPC, art. 319, VII"],
            position=position
        )
