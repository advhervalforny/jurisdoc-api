"""
Agente: Contestação Cível - Art. 335 CPC

⚠️ LEI 6: Este agente tem função única.
Gera assertions para contestações cíveis.

Base Legal:
- CPC, art. 335: Prazo e forma da contestação
- CPC, art. 336: Alegação de todas as defesas
- CPC, art. 337: Defesas processuais
"""
from typing import List, Dict

from app.cognitive.agents.base import (
    BaseAgent,
    GeneratedAssertion,
    NormalizedInput,
    register_agent
)
from app.models.assertion import LegalSource


@register_agent
class ContestacaoCivilAgent(BaseAgent):
    """
    Agente especializado em Contestações Cíveis.
    
    ⚠️ LEI 5: Produz assertions, NÃO texto final.
    """
    
    agent_id = "contestacao-civil"
    name = "Agente Contestação Cível – Art. 335 CPC"
    legal_basis = "CPC, art. 335"
    legal_area = "civil"
    piece_type = "Contestação"
    
    async def generate(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """
        Gera assertions para contestação.
        
        Estrutura da contestação:
        - Tempestividade
        - Preliminares (se houver)
        - Dos fatos
        - Do direito
        - Dos pedidos
        """
        assertions = []
        position = 0
        
        # ===== TEMPESTIVIDADE =====
        position += 1
        assertions.append(GeneratedAssertion(
            text="A presente contestação é tempestiva, apresentada dentro do prazo legal de 15 (quinze) dias úteis, conforme art. 335 do CPC.",
            assertion_type="fato",
            confidence_level="alto",
            suggested_sources=["CPC, art. 335"],
            position=position
        ))
        
        # ===== PRELIMINARES (análise dos fatos) =====
        preliminares = self._analyze_preliminares(input_data, sources)
        for prelim in preliminares:
            position += 1
            prelim.position = position
            assertions.append(prelim)
        
        # ===== DOS FATOS =====
        position += 1
        assertions.append(GeneratedAssertion(
            text="Cabe ao réu manifestar-se precisamente sobre os fatos narrados na petição inicial, presumindo-se verdadeiros os fatos não impugnados, nos termos do art. 341 do CPC.",
            assertion_type="fundamento",
            confidence_level="alto",
            suggested_sources=["CPC, art. 341"],
            position=position
        ))
        
        # Impugnação dos fatos
        for i, fato in enumerate(input_data.fatos):
            position += 1
            assertions.append(GeneratedAssertion(
                text=f"Impugna-se expressamente a alegação de que \"{fato}\", por não corresponder à verdade dos fatos.",
                assertion_type="fato",
                confidence_level="medio",  # Médio porque depende de prova
                suggested_sources=[],
                position=position
            ))
        
        # ===== DO DIREITO =====
        fundamentos = self._generate_fundamentos_defesa(input_data, sources)
        for fund in fundamentos:
            position += 1
            fund.position = position
            assertions.append(fund)
        
        # ===== DOS PEDIDOS =====
        position += 1
        assertions.append(GeneratedAssertion(
            text="Requer seja acolhida a presente contestação para julgar IMPROCEDENTES os pedidos formulados na inicial.",
            assertion_type="pedido",
            confidence_level="alto",
            suggested_sources=["CPC, art. 336"],
            position=position
        ))
        
        # Provas
        position += 1
        assertions.append(GeneratedAssertion(
            text="Requer a produção de todas as provas em direito admitidas, especialmente a documental, testemunhal e pericial.",
            assertion_type="pedido",
            confidence_level="alto",
            suggested_sources=[],
            position=position
        ))
        
        # Honorários
        position += 1
        assertions.append(GeneratedAssertion(
            text="Requer a condenação do autor ao pagamento das custas processuais e honorários advocatícios.",
            assertion_type="pedido",
            confidence_level="alto",
            suggested_sources=["CPC, art. 85"],
            position=position
        ))
        
        return assertions
    
    def _analyze_preliminares(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """
        Analisa possíveis preliminares.
        
        Art. 337 CPC: defesas processuais.
        """
        preliminares = []
        
        # Verificar se CPC art. 337 está disponível
        if "CPC, art. 337" in sources:
            # Adicionar nota sobre preliminares
            preliminares.append(GeneratedAssertion(
                text="Antes de adentrar ao mérito, cumpre ao réu arguir eventuais questões processuais, nos termos do art. 337 do CPC.",
                assertion_type="fundamento",
                confidence_level="alto",
                suggested_sources=["CPC, art. 337"],
                position=0
            ))
        
        # Análise básica dos fatos para sugerir preliminares
        fatos_lower = " ".join(input_data.fatos).lower()
        
        # Ilegitimidade passiva
        if "empresa" in fatos_lower or "pessoa jurídica" in fatos_lower:
            preliminares.append(GeneratedAssertion(
                text="Em preliminar, arguição de ilegitimidade passiva ad causam, vez que o réu não possui relação jurídica com os fatos narrados na inicial.",
                assertion_type="tese",
                confidence_level="baixo",  # Baixo - precisa ser verificado
                suggested_sources=["CPC, art. 337, XI"],
                position=0
            ))
        
        return preliminares
    
    def _generate_fundamentos_defesa(
        self,
        input_data: NormalizedInput,
        sources: Dict[str, LegalSource]
    ) -> List[GeneratedAssertion]:
        """Gera fundamentos da defesa."""
        fundamentos = []
        
        # Ônus da prova
        fundamentos.append(GeneratedAssertion(
            text="O ônus da prova incumbe ao autor, quanto ao fato constitutivo de seu direito, conforme art. 373, I, do CPC.",
            assertion_type="fundamento",
            confidence_level="alto",
            suggested_sources=["CPC, art. 373"],
            position=0
        ))
        
        # Improcedência por falta de provas
        fundamentos.append(GeneratedAssertion(
            text="Na ausência de comprovação dos fatos constitutivos do direito alegado, impõe-se a improcedência dos pedidos.",
            assertion_type="tese",
            confidence_level="alto",
            suggested_sources=[],
            position=0
        ))
        
        # Se há alegação de dano moral
        fatos_lower = " ".join(input_data.fatos).lower()
        if "dano moral" in fatos_lower or "indenização" in fatos_lower:
            fundamentos.append(GeneratedAssertion(
                text="Inexiste dano moral indenizável, sendo certo que mero aborrecimento ou dissabor do cotidiano não configura dano moral.",
                assertion_type="tese",
                confidence_level="medio",
                suggested_sources=[],
                position=0
            ))
        
        return fundamentos
