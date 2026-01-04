"""
Service de Renderização de Documentos.

⚠️ LEI 4: Texto final é DERIVADO, nunca primário.

Este service transforma assertions em texto final renderizado.
O texto é sempre reconstruível a partir das assertions.
"""
from typing import Optional, List
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.models.document import LegalDocument, LegalDocumentVersion
from app.models.assertion import LegalAssertion, AssertionSource, AssertionType
from app.models.rendering import DocumentRendering, RenderFormat
from app.models.activity_log import LogActions, EntityTypes
from app.services.base import BaseService, log_activity
from app.services.assertion_service import assertion_service
from app.core.constitution import (
    ConstitutionViolation,
    validate_rendering_has_sources
)


class RenderingService(BaseService[DocumentRendering]):
    """
    Service para Renderização de Documentos.
    
    ⚠️ LEI 4: Texto final é DERIVADO
    
    O texto renderizado é uma "visão" das assertions.
    Pode ser regenerado a qualquer momento.
    A fonte da verdade são as assertions, não o texto renderizado.
    """
    
    def __init__(self):
        super().__init__(DocumentRendering)
    
    async def render_version(
        self,
        db: AsyncSession,
        user_id: UUID,
        version_id: UUID,
        render_format: RenderFormat = RenderFormat.MARKDOWN
    ) -> DocumentRendering:
        """
        Renderiza uma versão do documento.
        
        ⚠️ LEI 4: Texto final é derivado
        
        Validações:
        - Versão existe e pertence ao usuário
        - Todas as assertions têm fontes (LEI 2)
        
        Args:
            version_id: ID da versão a renderizar
            render_format: Formato de saída (markdown, html, etc)
        
        Returns:
            DocumentRendering com texto gerado
        """
        # Buscar versão com assertions
        version = await self._get_version_with_assertions(db, version_id, user_id)
        if not version:
            raise ValueError(f"Versão '{version_id}' não encontrada")
        
        # ⚠️ Validar que assertions têm fontes (LEI 2)
        is_valid, errors = await assertion_service.validate_version_juridically(db, version_id)
        if not is_valid:
            raise ConstitutionViolation(
                f"Não é possível renderizar versão com assertions inválidas: {errors}"
            )
        
        # Gerar texto baseado nas assertions
        rendered_text = await self._generate_rendered_text(version.assertions, render_format)
        
        # Verificar se já existe rendering para esta versão/formato
        existing = await self._get_existing_rendering(db, version_id, render_format)
        if existing:
            # Atualizar existente
            existing.rendered_text = rendered_text
            await db.commit()
            await db.refresh(existing)
            rendering = existing
        else:
            # Criar novo
            rendering = DocumentRendering(
                document_version_id=version_id,
                rendered_text=rendered_text,
                render_format=render_format
            )
            db.add(rendering)
            await db.commit()
            await db.refresh(rendering)
        
        # Log de auditoria
        await log_activity(
            db=db,
            user_id=user_id,
            action=LogActions.RENDER_DOCUMENT,
            entity_type=EntityTypes.RENDERING,
            entity_id=rendering.id,
            details={
                "version_id": str(version_id),
                "format": render_format.value,
                "assertions_count": len(version.assertions)
            }
        )
        
        return rendering
    
    async def get_rendering(
        self,
        db: AsyncSession,
        version_id: UUID,
        render_format: RenderFormat = RenderFormat.MARKDOWN
    ) -> Optional[DocumentRendering]:
        """
        Busca rendering existente para versão/formato.
        
        Retorna None se não existir (precisa chamar render_version).
        """
        return await self._get_existing_rendering(db, version_id, render_format)
    
    async def get_version_renderings(
        self,
        db: AsyncSession,
        version_id: UUID
    ) -> List[DocumentRendering]:
        """Lista todos os renderings de uma versão."""
        statement = (
            select(DocumentRendering)
            .where(DocumentRendering.document_version_id == version_id)
            .order_by(DocumentRendering.render_format)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def regenerate_rendering(
        self,
        db: AsyncSession,
        user_id: UUID,
        rendering_id: UUID
    ) -> DocumentRendering:
        """
        Regenera um rendering existente.
        
        Útil quando assertions foram modificadas.
        """
        # Buscar rendering
        statement = (
            select(DocumentRendering)
            .where(DocumentRendering.id == rendering_id)
        )
        result = await db.execute(statement)
        rendering = result.scalar_one_or_none()
        
        if not rendering:
            raise ValueError(f"Rendering '{rendering_id}' não encontrado")
        
        # Chamar render_version (que atualiza o existente)
        return await self.render_version(
            db=db,
            user_id=user_id,
            version_id=rendering.document_version_id,
            render_format=rendering.render_format
        )
    
    async def delete_rendering(
        self,
        db: AsyncSession,
        rendering_id: UUID
    ) -> bool:
        """
        Deleta rendering.
        
        ⚠️ LEI 4: Isso é permitido pois texto é derivado.
        O rendering pode ser regenerado a qualquer momento.
        """
        statement = select(DocumentRendering).where(DocumentRendering.id == rendering_id)
        result = await db.execute(statement)
        rendering = result.scalar_one_or_none()
        
        if not rendering:
            return False
        
        await db.delete(rendering)
        await db.commit()
        return True
    
    async def _generate_rendered_text(
        self,
        assertions: List[LegalAssertion],
        render_format: RenderFormat
    ) -> str:
        """
        Gera texto a partir das assertions.
        
        ⚠️ LEI 4: Texto é DERIVADO das assertions.
        Não adiciona conteúdo novo.
        """
        if render_format == RenderFormat.MARKDOWN:
            return self._render_markdown(assertions)
        elif render_format == RenderFormat.HTML:
            return self._render_html(assertions)
        else:
            # Default to markdown
            return self._render_markdown(assertions)
    
    def _render_markdown(self, assertions: List[LegalAssertion]) -> str:
        """Renderiza assertions em Markdown."""
        sections = {
            AssertionType.FATO: [],
            AssertionType.FUNDAMENTO: [],
            AssertionType.TESE: [],
            AssertionType.PEDIDO: []
        }
        
        # Agrupar por tipo
        for assertion in sorted(assertions, key=lambda a: a.position):
            sections[assertion.assertion_type].append(assertion)
        
        parts = []
        
        # DOS FATOS
        if sections[AssertionType.FATO]:
            parts.append("## DOS FATOS\n")
            for a in sections[AssertionType.FATO]:
                parts.append(f"{a.assertion_text}\n")
            parts.append("")
        
        # DO DIREITO / FUNDAMENTOS
        if sections[AssertionType.FUNDAMENTO] or sections[AssertionType.TESE]:
            parts.append("## DO DIREITO\n")
            
            for a in sections[AssertionType.FUNDAMENTO]:
                parts.append(f"{a.assertion_text}\n")
            
            for a in sections[AssertionType.TESE]:
                parts.append(f"{a.assertion_text}\n")
            parts.append("")
        
        # DOS PEDIDOS
        if sections[AssertionType.PEDIDO]:
            parts.append("## DOS PEDIDOS\n")
            parts.append("Ante o exposto, requer:\n")
            for i, a in enumerate(sections[AssertionType.PEDIDO], 1):
                parts.append(f"{i}. {a.assertion_text}\n")
            parts.append("")
        
        return "\n".join(parts)
    
    def _render_html(self, assertions: List[LegalAssertion]) -> str:
        """Renderiza assertions em HTML."""
        sections = {
            AssertionType.FATO: [],
            AssertionType.FUNDAMENTO: [],
            AssertionType.TESE: [],
            AssertionType.PEDIDO: []
        }
        
        # Agrupar por tipo
        for assertion in sorted(assertions, key=lambda a: a.position):
            sections[assertion.assertion_type].append(assertion)
        
        parts = ["<article class='legal-document'>"]
        
        # DOS FATOS
        if sections[AssertionType.FATO]:
            parts.append("<section class='fatos'>")
            parts.append("<h2>DOS FATOS</h2>")
            for a in sections[AssertionType.FATO]:
                parts.append(f"<p>{a.assertion_text}</p>")
            parts.append("</section>")
        
        # DO DIREITO
        if sections[AssertionType.FUNDAMENTO] or sections[AssertionType.TESE]:
            parts.append("<section class='direito'>")
            parts.append("<h2>DO DIREITO</h2>")
            
            for a in sections[AssertionType.FUNDAMENTO]:
                parts.append(f"<p>{a.assertion_text}</p>")
            
            for a in sections[AssertionType.TESE]:
                parts.append(f"<p>{a.assertion_text}</p>")
            parts.append("</section>")
        
        # DOS PEDIDOS
        if sections[AssertionType.PEDIDO]:
            parts.append("<section class='pedidos'>")
            parts.append("<h2>DOS PEDIDOS</h2>")
            parts.append("<p>Ante o exposto, requer:</p>")
            parts.append("<ol>")
            for a in sections[AssertionType.PEDIDO]:
                parts.append(f"<li>{a.assertion_text}</li>")
            parts.append("</ol>")
            parts.append("</section>")
        
        parts.append("</article>")
        return "\n".join(parts)
    
    async def _get_version_with_assertions(
        self,
        db: AsyncSession,
        version_id: UUID,
        user_id: UUID
    ) -> Optional[LegalDocumentVersion]:
        """Busca versão com assertions carregadas."""
        statement = (
            select(LegalDocumentVersion)
            .join(LegalDocument)
            .join(Case)
            .options(
                selectinload(LegalDocumentVersion.assertions)
                .selectinload(LegalAssertion.source_links)
                .selectinload(AssertionSource.source)
            )
            .where(LegalDocumentVersion.id == version_id)
            .where(Case.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()
    
    async def _get_existing_rendering(
        self,
        db: AsyncSession,
        version_id: UUID,
        render_format: RenderFormat
    ) -> Optional[DocumentRendering]:
        """Busca rendering existente."""
        statement = (
            select(DocumentRendering)
            .where(DocumentRendering.document_version_id == version_id)
            .where(DocumentRendering.render_format == render_format)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()


# Instância singleton
rendering_service = RenderingService()
